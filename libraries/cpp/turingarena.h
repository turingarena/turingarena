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
    }

    struct ResourceUsage {
        float time_usage;
        int memory_usage;
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

            driver_downward << "wait\n0" << std::endl;

            ResourceUsage rusage;

            driver_upward >> rusage.time_usage;
            driver_upward >> rusage.memory_usage;

            return rusage;
        }

        void send_exit_request()
        {
            driver_downward << "request\n";
            driver_downward << "exit" << std::endl;
        }

        void send_callback_return(bool has_return_value, int return_value = 0) 
        {
            get_response_ok();

            driver_downward << "request\n";
            driver_downward << "callback_return\n";
            driver_downward << has_return_value << '\n';
            driver_downward << return_value << std::endl;
        }

        void get_response_ok()
        {
            int error;
            driver_upward >> error;
            if (error) {
                throw std::runtime_error("Something bad occurred!");
            }
        }

        template <int i, typename Ret, typename ...Params, typename ...Args>
        typename std::enable_if<i == sizeof...(Params) && std::is_void<Ret>::value, void>::type
        call_n_args(std::function<Ret(Params...)> function, Args ...args)
        {
            function(args...);
            send_callback_return(false);
        }

        template <int i, typename Ret, typename ...Params, typename ...Args>
        typename std::enable_if<i == sizeof...(Params) && !std::is_void<Ret>::value, void>::type
        call_n_args(std::function<Ret(Params...)> function, Args ...args)
        {
            int res = function(args...);
            send_callback_return(true, res);
        }


        template <int i, typename Ret, typename ...Params, typename ...Args>
        typename std::enable_if<(i < sizeof...(Params)), void>::type
        call_n_args(std::function<Ret(Params...)> function, Args ...args)
        {
            int arg;
            driver_upward >> arg;
            return call_n_args<i + 1>(function, args..., arg);
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

                if (!has_callbacks)
                    break;

                int index;
                driver_upward >> index;

                std::cerr << "GOT CALLBACK REQUEST: i = " << index << std::endl;

                call_n_callback<0>(callbacks, index); 
            }
        }

        template <typename ...Args, typename ...Callbacks>
        int call(const std::string& name, bool has_return_value, std::tuple<Args...> args, std::tuple<Callbacks...> callbacks)
        {
            
            get_response_ok();

            driver_downward << "request\n";
            driver_downward << "call\n";
            driver_downward << name << '\n';
            driver_downward << sizeof...(Args) << '\n';
            put_args<0>(args);

            driver_downward << has_return_value << '\n';
            driver_downward << sizeof...(Callbacks) << '\n';
            driver_downward << 1 << '\n';
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

        ~Algorithm()
        {
            send_exit_request();
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