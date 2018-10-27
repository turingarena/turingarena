#ifndef TURINGARENA_H
#define TURINGARENA_H

#include <string>
#include <fstream>
#include <algorithm>
#include <cstdlib>
#include <unistd.h>
#include <cctype>
#include <iostream>
#include <tuple>
#include <functional>

#include <cassert>

namespace turingarena {

    namespace {
        inline std::string get_submission_parameter(const std::string& name)
        {
            std::string variable_name = std::string("SUBMISSION_FILE_") + name;        
            std::transform(variable_name.begin(), variable_name.end(), variable_name.begin(), toupper);
            const char *result = getenv(variable_name.c_str());
            if (result == nullptr) {
                throw std::runtime_error{"Invalid variable"};
            }
            return std::string(result);
        }

        inline std::string get_cwd() 
        {
            char buff[1024];
            getcwd(buff, sizeof buff);
            return std::string(buff);
        }

        inline void evaluation_data(const std::string& data)
        {
            static const char *evaluation_data_begin = getenv("EVALUATION_DATA_BEGIN");
            static const char *evaluation_data_end = getenv("EVALUATION_DATA_END");

            std::cout << evaluation_data_begin << data << evaluation_data_end << std::endl;
        }

        struct {
            std::string operator[](const std::string& key) {
                return get_submission_parameter(key);
            }
        } submission;
    }

    struct ResourceUsage {
        float time_usage;
        int memory_usage;
    };


    template <typename T>
    struct function_traits : public function_traits<decltype(&T::operator())> {};

    template <typename ClassType, typename ReturnType, typename... Args>
    struct function_traits<ReturnType(ClassType::*)(Args...) const> {
        enum { arity = sizeof...(Args) };
        typedef ReturnType result_type;
    };

    class Algorithm {
        std::string sandbox_dir;
        std::string sandbox_process_dir;
        std::ofstream driver_downward;
        std::ifstream driver_upward;

        std::string status;

        // this is a specialization only for scalar types
        template <typename T>
        typename std::enable_if<std::is_scalar<T>::value, void>::type
        put_arg(T arg)
        {
            driver_downward << "0\n"; // scalar
            driver_downward << arg << '\n';
        }

        // this is a specialization for non scalar types (arrays, and if not fail)
        template <typename T>
        typename std::enable_if<!std::is_scalar<T>::value, void>::type
        put_arg(T arg)
        {
            driver_downward << "1\n"; // array
            driver_downward << arg.end() - arg.begin() << '\n';
            
            for (const auto& e : arg) {
                put_arg(e);
            }
        }

        // base case
        template <int i, typename ...Args>
        typename std::enable_if<i >= sizeof...(Args), void>::type
        put_args(std::tuple<Args...> args) {}

        // recursive template to send args
        template <int i, typename ...Args>
        typename std::enable_if<i < sizeof...(Args), void>::type
        put_args(std::tuple<Args...> args)
        {
            put_arg(std::get<i>(args));
            put_args<i + 1>(args);
        }

        ResourceUsage wait()
        {
            get_response_ok();

            driver_downward << "wait\n;";
            driver_downward << 0 << std::endl;

            ResourceUsage rusage;

            driver_upward >> rusage.time_usage;
            driver_upward >> rusage.memory_usage;

            return rusage;
        }

        void send_request(const std::string& request)
        {
            get_response_ok();

            driver_downward << "request\n";
            driver_downward << request << std::endl;
        }

        void send_callback_return(bool has_return_value, int return_value = 0) 
        {
            send_request("callback_return");

            driver_downward << has_return_value << '\n';
            driver_downward << return_value << std::endl;
        }

        void throw_exeption()
        {
            float time_usage;
            int memory_usage;
            std::string error_message;
            driver_upward >> time_usage;
            driver_upward >> memory_usage;
            std::getline(driver_upward, error_message);
            std::getline(driver_upward, error_message);
            std::cerr << "Error occurred\n";
            std::cerr << "Time Usage: " << time_usage << std::endl;
            std::cerr << "Memory Usage: " << memory_usage << std::endl;
            throw std::runtime_error("Driver error: " + error_message);
        }

        void get_response_ok()
        {
            int error;
            driver_upward >> error;
            if (error) 
                throw_exeption();
        }

        template <int i, typename Function, typename ...Args>
        typename std::enable_if<i == function_traits<Function>::arity && std::is_void<typename function_traits<Function>::result_type>::value, void>::type
        call_n_args(Function function, Args ...args)
        {
            function(args...);
            send_callback_return(false);
        }

        template <int i, typename Function, typename ...Args>
        typename std::enable_if<i == function_traits<Function>::arity && !std::is_void<typename function_traits<Function>::result_type>::value, void>::type
        call_n_args(Function function, Args ...args)
        {
            send_callback_return(true, function(args...));
        }

        template <int i, typename Function, typename ...Args>
        typename std::enable_if<(i < function_traits<Function>::arity), void>::type
        call_n_args(Function function, Args ...args)
        {
            int arg;
            driver_upward >> arg;
            call_n_args<i + 1>(function, args..., arg);
        }

        template <int i, typename ...Callbacks>
        typename std::enable_if<i == sizeof...(Callbacks), void>::type
        call_n_callback(std::tuple<Callbacks...> callbacks, int index)
        {}

        template <int i, typename ...Callbacks>
        typename std::enable_if<(i < sizeof...(Callbacks)), void>::type
        call_n_callback(std::tuple<Callbacks...> callbacks, int index)
        {
            if (index == i)
                call_n_args<0>(std::get<i>(callbacks));
            else
                call_n_callback<i + 1>(callbacks, index);
        }

        template <typename ...Callbacks>
        void accept_callbacks(std::tuple<Callbacks...> callbacks)
        {
            while (true) {
                int has_callbacks;
                driver_upward >> has_callbacks;

                if (has_callbacks == 0)
                    break;
                
                if (has_callbacks == -1)
                    throw_exeption();

                int index;
                driver_upward >> index;
                call_n_callback<0>(callbacks, index); 
            }
        }

        template <typename Function>
        void put_callback_n_args(Function function)
        {
            driver_downward << function_traits<Function>::arity << '\n';
        }

        template <int i, typename ...Callbacks>
        typename std::enable_if<i == sizeof...(Callbacks), void>::type
        put_callbacks_n_args(std::tuple<Callbacks...> callbacks)
        {}

        template <int i, typename ...Callbacks>
        typename std::enable_if<i < sizeof...(Callbacks), void>::type
        put_callbacks_n_args(std::tuple<Callbacks...> callbacks)
        {
            put_callback_n_args(std::get<i>(callbacks));
            put_callbacks_n_args<i + 1>(callbacks);
        }

        template <typename ...Args, typename ...Callbacks>
        int call(const std::string& name, bool has_return_value, std::tuple<Args...> args, std::tuple<Callbacks...> callbacks)
        {
            send_request("call");

            driver_downward << name << '\n';
            driver_downward << sizeof...(Args) << '\n';
            put_args<0>(args);

            driver_downward << has_return_value << '\n';
            driver_downward << sizeof...(Callbacks) << '\n';
            put_callbacks_n_args<0>(callbacks);
            driver_downward.flush();

            accept_callbacks(callbacks);

            int result = 0;
            if (has_return_value)
                driver_upward >> result;

            return result;
        }

    public:
        Algorithm(const Algorithm&) = delete;
        Algorithm& operator=(const Algorithm&) = delete;  

        Algorithm(const std::string& source_path) : 
            Algorithm(source_path, get_cwd() + "/interface.txt") {}

        Algorithm(const std::string& source_path, const std::string& interface_path) :
            sandbox_dir{getenv("TURINGARENA_SANDBOX_DIR")}
        {
            {
                std::ofstream language_name_pipe{sandbox_dir + "/language_name.pipe"};
                language_name_pipe << "";
            }

            {
                std::ofstream source_path_pipe{sandbox_dir + "/source_path.pipe"};
                source_path_pipe << source_path;
            }

            {
                std::ofstream interface_path_pipe{sandbox_dir + "/interface_path.pipe"};
                interface_path_pipe << interface_path;
            }

            {
                std::ifstream sandbox_process_dir_pipe{sandbox_dir + "/sandbox_process_dir.pipe"};
                sandbox_process_dir_pipe >> sandbox_process_dir;
            }

            driver_downward.open(sandbox_process_dir + "/driver_downward.pipe");
            driver_upward.open(sandbox_process_dir + "/driver_upward.pipe");
        }

        void exit()
        {
            send_request("exit");
        }

        void checkpoint()
        {
            send_request("checkpoint");
        }

        ~Algorithm()
        {
            exit();
        }

        template <typename ...Args, typename ...Callbacks>
        int call_function(const std::string& function_name, std::tuple<Callbacks...> callbacks, Args ...args)
        {
            return call(function_name, true, std::make_tuple(args...), callbacks);
        }

        template <typename ...Args>
        int call_function(const std::string& function_name, Args ...args)
        {
            return call(function_name, true, std::make_tuple(args...), std::make_tuple());
        }

        template <typename ...Args, typename ...Callbacks>
        void call_procedure(const std::string& procedure_name, std::tuple<Callbacks...> callbacks, Args ...args)
        {
            call(procedure_name, false, std::make_tuple(args...),callbacks);
        }

        template <typename ...Args>
        void call_procedure(const std::string& procedure_name, Args ...args)
        {
            call(procedure_name, false, std::make_tuple(args...), std::make_tuple());
        }

        ResourceUsage get_resource_usage() 
        {
            return wait();
        }

    };
};

#endif /* TURINGARENA_H */