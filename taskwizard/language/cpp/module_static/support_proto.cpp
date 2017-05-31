#include <bits/stdc++.h>
#include "support_proto.h"

#define MAX_LEN 200

#define trace(...) do { \
    fprintf(stderr, "supervisor client: "); \
    fprintf(stderr, __VA_ARGS__); \
  } while(0);

struct proc_handle_structure {
    int process_id;
    FILE *upward_pipe;
    FILE *downward_pipe;
};

FILE *control_request_pipe;
FILE *control_response_pipe;

FILE *process_upward_pipe(void *handle) {
    proc_handle_structure *handle_struct = (proc_handle_structure*) handle;
    return handle_struct->upward_pipe;
}

FILE *process_downward_pipe(void *handle) {
    proc_handle_structure *handle_struct = (proc_handle_structure*) handle;
    return handle_struct->downward_pipe;
}

void driver_init() {
    control_request_pipe = fopen("control_request.pipe", "w");
    control_response_pipe = fopen("control_response.pipe", "r");
}

void* algorithm_create_process(const char *algo_name) {
    // Start new process    
    trace("Creating new process for algorithm \"%s\"\n", algo_name);    
    fprintf(control_request_pipe, "algorithm_create_process %s\n", algo_name);
    fflush(control_request_pipe);
    int process_id;
    fscanf(control_response_pipe, "%d", &process_id);

    proc_handle_structure *handle_struct = new proc_handle_structure();
    memset(handle_struct, 0, sizeof(proc_handle_structure));
    handle_struct->process_id = process_id;

    return handle_struct;
}

static int read_status() {
    int status;
    fscanf(control_response_pipe, " %d", &status);
    trace("Status of request: %d\n", status);    
    return status;
}

int process_start(void *handle) {
    proc_handle_structure *handle_struct = (proc_handle_structure*) handle;

    trace("Starting process with id: %d...\n", handle_struct->process_id);
    fprintf(control_request_pipe, "process_start %d\n", handle_struct->process_id);
    fflush(control_request_pipe);
    
    int status = read_status();
    
    char process_downward_pipe_name[MAX_LEN];
    sprintf(process_downward_pipe_name, "process_downward.%d.pipe", handle_struct->process_id);

    char process_upward_pipe_name[MAX_LEN];
    sprintf(process_upward_pipe_name, "process_upward.%d.pipe", handle_struct->process_id);

    handle_struct->downward_pipe = fopen(process_downward_pipe_name, "w");
    handle_struct->upward_pipe = fopen(process_upward_pipe_name, "r");

    trace("successfully opened pipes of process %d\n", handle_struct->process_id);

    // Set auto flush
    setvbuf(handle_struct->downward_pipe, NULL, _IONBF, 0);
    
    return status;
}

int process_status(void *handle) {
    proc_handle_structure *handle_struct = (proc_handle_structure*) handle;
    trace("Requesting status of process with id: %d...\n", handle_struct->process_id);
    fprintf(control_request_pipe, "process_status %d\n", handle_struct->process_id);
    fflush(control_request_pipe);
    return read_status();
}

int process_stop(void *handle) {
    proc_handle_structure *handle_struct = (proc_handle_structure*) handle;    
    trace("Killing process with id: %d...\n", handle_struct->process_id);
    fprintf(control_request_pipe, "process_stop %d\n", handle_struct->process_id);
    fflush(control_request_pipe);
    return read_status();
}
