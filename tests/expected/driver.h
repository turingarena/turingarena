#include "driver_support_common.h"

class exampleinterface : support::interface {
    int value_N;
    bool is_set_N;

    int value_M;
    bool is_set_M;

    int *value_A;
    bool *is_set_A;

    int downward_index_i;
    int upward_index_i;

    enum {
        state_call_solve,
    } downward_state, upward_state;

    void validate() const {
        try {
            check_valid(get_N() * get_N() <= get_M());
        } catch(value_not_set e) {}
    }

    void advance_downward() {
        switch(downward_state) {
        case state_call_solve: goto label_call_solve;
        }

        fprintf(downward_pipe(), "%d %d\n", get_N(), get_M());
        int& idx_i = downward_index_i;
        for(idx_i = 1; idx_i <= get_N(); idx_i++) {
            fprintf(downward_pipe(), "%d\n", get_A(idx_i));
        }

        downward_state = state_call_solve;
        return;
        label_call_solve: ;
    }

    void advance_upward() {
        fflush(downward_pipe());

        switch(upward_state) {
        case state_call_solve: goto label_call_solve;
        }

        int& idx_i = upward_index_i;
        for(idx_i = 1; idx_i <= get_N(); idx_i++) {
        }

        upward_state = state_call_solve;
        return;
        label_call_solve: ;
        fscanf(upward_pipe(), "%d", &S);
    }

    void check_protocol_sync() {
        if(downward_state != upward_state) fail_protocol_out_of_sync();
        if(downward_index_i != upward_index_i) fail_protocol_out_of_sync();
    }

public:
    void set_N(int value) {
        check_not_set(!is_set_N, "N");

        value_N = value;
        is_set_N = true;
    }

    int get_N() const {
        check_set(is_set_N, "N");

        return value_N;
    }

    void set_M(int value) {
        check_not_set(!is_set_M, "M");

        value_M = value;
        is_set_M = true;
    }

    int get_M() const {
        check_set(is_set_M, "M");

        return value_M;
    }

    int index_min_A() const {
        return 1;
    }

    int index_max_A() const {
        return get_N();
    }

    void create_A() {
        check_not_created(!value_A, "A");

        size_t size = index_max_A() + 1;
        value_A = new int[size];
        is_set_A = new bool[size];
    }

    void set_A(int idx_i, int value) {
        check_created(value_A, "A");
        check_index_min(idx_i >= index_min_A(), "A", idx_i);
        check_index_max(idx_i <= index_max_A(), "A", idx_i);

        check_not_set(!is_set_A[idx_i], "A");

        value_A[idx_i] = value;
        is_set_A[idx_i] = true;
    }

    int get_A(int idx_i) const {
        check_created(value_A, "A");
        check_index_min(idx_i >= index_min_A(), "A", idx_i);
        check_index_max(idx_i <= index_max_A(), "A", idx_i);

        check_set(is_set_A[idx_i], "A");

        return value_A[idx_i];
    }

    void send_call_solve(int param_N, int param_M) {
        if(!is_set_N) set_N(param_N);
        check_matching(get_N() == param_N, "N", "N");

        if(!is_set_M) set_M(param_M);
        check_matching(get_M() == param_M, "M", "M");

        advance_downward();
        if(downward_state != state_call_solve) fail_unexpected_call("solve");
    }

    int wait_call_solve(int param_N, int param_M) {
        if(upward_state != state_call_solve) fail_unexpected_call("solve");
        advance_upward();

        return get_S();
    }

    int call_solve(int param_N, int param_M) {
        send_call_solve(param_N, param_M);
        check_protocol_sync();
        return wait_call_solve(param_N, param_M);
    }

};
