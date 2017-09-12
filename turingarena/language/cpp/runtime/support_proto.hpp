#include <string>
#include <cstdio>
#include <fstream>
#include <sstream>
#include <memory>

namespace taskwizard {

class Supervisor;

class Process {
    Supervisor& supervisor;
    int process_id;
    std::string algorithm_name;
    FILE* downward_pipe;
    FILE* upward_pipe;

    Process(Supervisor& _supervisor, int _process_id, std::string _algorithm_name);

    friend class Supervisor;

public:

    FILE* get_dowward_pipe() {
        return downward_pipe;
    }

    FILE* get_upward_pipe() {
        return upward_pipe;
    }
};

class Supervisor {
    std::string sandbox_dir;
    std::ofstream request;
    std::ifstream response;

    friend class Process;

public:
    Supervisor(std::string _sandbox_dir)
        :
        sandbox_dir(_sandbox_dir),
        request((sandbox_dir + "/control_request.pipe").c_str()),
        response((sandbox_dir + "/control_response.pipe").c_str())
    {}

    Process algorithm_create_process(std::string algorithm_name) {
        int process_id;

        request << "algorithm_create_process " << algorithm_name << std::endl;
        response >> process_id;

        return Process(*this, process_id, algorithm_name);
    }

    void trace() {
    }
};

inline std::unique_ptr<Supervisor> default_supervisor() {
    return std::unique_ptr<Supervisor>(new Supervisor(getenv("TASKWIZARD_SANDBOX_DIR")));
}

inline Process::Process(Supervisor& _supervisor, int _process_id, std::string _algorithm_name)
    :
    supervisor(_supervisor),
    process_id(_process_id),
    algorithm_name(_algorithm_name)
{
    std::stringstream downward_pipe_name;
    downward_pipe_name << supervisor.sandbox_dir << "/process_downward." << process_id << ".pipe";
    downward_pipe = fopen(downward_pipe_name.str().c_str(), "w");

    std::stringstream upward_pipe_name;
    upward_pipe_name << supervisor.sandbox_dir << "/process_upward." << process_id << ".pipe";
    upward_pipe = fopen(downward_pipe_name.str().c_str(), "r");
}

}