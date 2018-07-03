#ifndef TURINGARENA_H
#define TURINGARENA_H

#include <string>
#include <fstream>
#include <algorithm>
#include <cstdlib>
#include <unistd.h>
#include <cctype>
#include <iostream>

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

    class Algorithm {
        std::string sandbox_dir;
        std::string sandbox_process_dir;
        std::ofstream driver_downward;
        std::ifstream driver_upward;

        std::string status;
        int memory_usage;
        int time_usage;

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
        void put_args() {}

        // recursive function to send args
        template <typename First, typename ...Others>
        void put_args(First first, Others ...others)
        {
            put_arg(first);
            put_args(others...);
        }

        void read_status()
        {
            std::string has_callbacks;

            driver_upward >> status;
            driver_upward >> has_callbacks;
        }

        void read_resource_usage()
        {
            driver_downward << "wait\n";
            driver_downward << "0\n";
            driver_downward.flush();

            driver_upward >> time_usage;
            driver_upward >> memory_usage;
        }

        void send_exit_request()
        {
            driver_downward << "request\n";
            driver_downward << "exit\n";
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

        template <typename ...Args>
        int call_function(const std::string& function_name, Args ...args)
        {
            int result;
            
            driver_downward << "request\n";
            driver_downward << "call\n";
            driver_downward << function_name << '\n';
            driver_downward << sizeof...(Args) << '\n';
            put_args(args...);

            driver_downward << 1 << '\n'; // 1 = function
            driver_downward << 0 << '\n'; // no callbacks
            driver_downward.flush();

            read_status();

            driver_upward >> result;

            read_resource_usage();

            return result;
        }

        template <typename ...Args>
        void call_procedure(const std::string& procedure_name, Args ...args)
        {
            driver_downward << "request\n";
            driver_downward << "call\n";
            driver_downward << procedure_name << '\n';
            driver_downward << sizeof...(Args) << '\n';
            put_args(args...);

            driver_downward << "0\n"; // 0 = procedure
            driver_downward << "0\n"; // no callbacks
            driver_downward.flush();

            read_status();
            read_resource_usage();
        }

        int get_memory_usage() { return memory_usage; }
        int get_time_usage() { return time_usage; }

    };
};

#endif /* TURINGARENA_H */