#ifndef TURINGARENA_H
#define TURINGARENA_H

#include <string>
#include <fstream>

namespace turingarena {
    std::string sandbox_dir;
    std::string sandbox_process_dir;
    std::ofstream driver_downward;
    std::ifstream driver_upward;

    std::string status;
    int memory_usage;
    int time_usage;

    class Algorithm {

        // base case
        void put_args() {}

        template <typename First, typename ...Others>
        void put_args(int first, Others ...others)
        {
            driver_downward << "0\n"; // scalar
            driver_downward << first << '\n';
            put_arg(others...);
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

            driver_upward >> time_usage;
            driver_upward >> memory_usage;
        }

    public:
        Algorithm(const std::string& source_path, const std::string& interface_path)
        {
            sandbox_dir = getenv("TURINGARENA_SANDBOX_DIR");

            {
                std::ofstream language_name_pipe{sandbox_dir + "/language_name.pipe"};
                language_name_pipe << "";
            }

            {
                std::ofstream interface_path_pipe{sandbox_dir + "/interface_path.pipe"};
                interface_path_pipe << interface_path;
            }

            {
                std::ofstream source_path_pipe{sandbox_dir + "/source_path.pipe"};
                source_path_pipe << source_path;
            }

            {
                std::ifstream sandbox_process_dir_pipe{sandbox_dir + "/sandobox_process_dir.pipe"};
                sandbox_process_dir_pipe >> sandbox_process_dir;
            }

            std::cerr << "Executing algorithm process_dir = " << sandbox_process_dir << std::endl;

            driver_downward.open(sandbox_process_dir + "/driver_downward.pipe");
            driver_upward.open(sandbox_process_dir + "/driver_upward.pipe");

        }

        ~Algorithm()
        {
            exit();
        }

        template <typename ...Types>
        int call_function(const std::string& function_name, Args ...args)
        {
            int result;

            driver_downward << "request\n";
            driver_downward << "call\n";
            driver_downward << function_name << '\n';
            driver_downward << sizeof...(Args) << '\n';
            put_args(args);

            driver_downward << 1 << '\n'; // 1 = function
            driver_downward << 0 << '\n'; // no callbacks
            driver_downward.flush();

            read_status();

            driver_upward >> result;

            read_resource_usage();

            return result;
        }

        template <typename ...Types>
        void call_procedure(const std::string& procedure_name, Args ...args)
        {
            driver_downward << "request\n";
            driver_downward << "call\n";
            driver_downward << procedure_name << '\n';
            driver_downward << sizeof...(Args) << '\n';
            put_args(args);

            driver_downward << "0\n"; // 0 = procedure
            driver_downward << "0\n"; // no callbacks
            driver_downward.flush();

            read_status();
            read_resource_usage();
        }


        int exit()
        {
            driver_downward << "request\n";
            driver_downward << "exit\n";
        }

        int get_memory_usage() { return memory_usage; }
        int get_time_usage() { return time_usage; }

    };
};

#endif /* TURINGARENA_H */