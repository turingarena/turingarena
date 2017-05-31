#include <cstdio>

namespace support {

class interface {
    void* process_handle;

protected:
    FILE* upward_pipe() {
        return process_upward_pipe(process_handle);
    }

    FILE* downward_pipe() {
        return process_downward_pipe(process_handle);
    }

    class value_not_set : std::logic_error {
        value_not_set(std::string name) : std::domain_error(name) {}
    }

    void check_set(bool ok, std::string name) {
        if(ok) return;
        throw value_not_set(name);
    }

    void check_not_set(bool ok, std::string name) {
        if(ok) return;
        throw std::logic_error(std::string() + "Value already set: " + name));
    }

    void check_created(bool ok, std::string name) {
        if(ok) return;
        throw std::logic_error(std::string() + "Array not created: " + name));
    }

    void check_not_created(bool ok, std::string name) {
        if(ok) return;
        throw std::logic_error(std::string() + "Array already created: " + name));
    }

    void fail_protocol_out_of_sync() {
        throw std::logic_error(std::string() + "Input/output protocols out of sync"));
    }

}

}