#include <bits/stdc++.h>
#include "support_proto.h"

#define trace(...) do { \
    fprintf(stderr, "DRIVER({{driver.name}}): supervisor client: "); \
    fprintf(stderr, __VA_ARGS__); \
  } while(0);

struct interface_common_data;
struct proc_handle_structure {
    int process_id;
    FILE *upward_pipe;
    FILE *downward_pipe;
    interface_common_data *common_data;
    void *interface_data;
};

//FILE *read_file_pipes[2000];
//FILE *write_file_pipes[2000];

FILE *control_request_pipe;
FILE *control_response_pipe;

FILE *parameter_file;
int seed;

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

    parameter_file = fopen("parameter.txt", "r");
    
    FILE *seed_file = fopen("seed.txt", "r");
    trace("Reading seed...\n");    
    fscanf(seed_file, "%d", &seed);
    trace("Seed: %d.\n", seed);    
    fclose(seed_file);
}

int get_seed() {
    return seed;
}

FILE* get_parameter_file() {
    return parameter_file;
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
    
    char process_downward_pipe_name[200];
    sprintf(process_downward_pipe_name, "process_downward.%d.pipe", handle_struct->process_id);

    char process_upward_pipe_name[200];
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

/*int read_file_open(const char *file_name) {
    
    // Open file for reading
    trace("Opening file with name: \"%s\"...\n", file_name);    
    fprintf(control_request_pipe, "read_file_open %s\n", file_name);
    fflush(control_request_pipe);
    int descriptor;
    fscanf(control_response_pipe, " %d", &descriptor);
    

    // Generate file names
    char read_file_name[200];
    sprintf(read_file_name, "read_file.%d.txt", descriptor);

    // Open descriptors
    read_file_pipes[descriptor] = fopen(read_file_name, "r");    
    return descriptor;  
}

FILE *read_file_pipe(int id) {
    trace("Requested id %d with pointer: %p\n", id, read_file_pipes[id]);
    return read_file_pipes[id];
}

int read_file_close(int id) {

    if (read_file_pipes[id]) {
        fclose(read_file_pipes[id]);
        read_file_pipes[id] = NULL;

        trace("Closing pipe with id %d\n", id);
        fprintf(control_request_pipe, "read_file_close %d\n", id);
        fflush(control_request_pipe);
        return read_status();
    }

    trace("Driver requested to close an invalid file with id: %d\n", id);    
}

int write_file_open(const char *file_name) {
    return -1; // TODO
}

FILE *write_file_pipe(int id) {
    return NULL; // TODO
}

int write_file_close(int id) {
    return -1; // TODO
}*/
