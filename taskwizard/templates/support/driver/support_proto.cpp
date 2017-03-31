#include <bits/stdc++.h>
#include "support_proto.h"

FILE *process_upward_pipes[2000];
FILE *process_downward_pipes[2000];

FILE *read_file_pipes[2000];
FILE *write_file_pipes[2000];

FILE *control_request_pipe;
FILE *control_response_pipe;

FILE *parameter_file;
int seed;

FILE *process_upward_pipe(int id) {
    return process_upward_pipes[id];
}

FILE *process_downward_pipe(int id) {
    return process_downward_pipes[id];
}

<<<<<<< HEAD
int algorithm_start(const char *algo_name) {
    // Start new algorithm    
    fprintf(stderr, "DRIVER SUPERVISOR CLIENT: Starting new instance of algorithm \"%s\"\n", algo_name);    
    printf("algorithm_start %s\n", algo_name);
    fflush(control_request_pipe);
    int descriptor;
    scanf("%d", &descriptor);
=======
#define trace(...) do { \
    fprintf(stderr, "DRIVER({{driver.name}}): supervisor client: "); \
    fprintf(stderr, __VA_ARGS__); \
  } while(0);

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

int algorithm_create_process(const char *algo_name) {
    // Start new process    
    trace("Creating new process for algorithm \"%s\"\n", algo_name);    
    fprintf(control_request_pipe, "algorithm_create_process %s\n", algo_name);
    fflush(control_request_pipe);
    int process_id;
    fscanf(control_response_pipe, "%d", &process_id);
>>>>>>> 4b54911449a8d29736c62151628488d705380a86

    return process_id;
}

static int read_status() {
    int status;
    fscanf(control_response_pipe, " %d", &status);
    trace("Status of request: %d\n", status);    
    return status;
}

int process_start(int process_id) {
    trace("Starting process with id: %d...\n", process_id);
    fprintf(control_request_pipe, "process_start %d\n", process_id);
    fflush(control_request_pipe);
    
    int status = read_status();
    
    char process_downward_pipe_name[200];
    sprintf(process_downward_pipe_name, "process_downward.%d.pipe", process_id);

    char process_upward_pipe_name[200];
    sprintf(process_upward_pipe_name, "process_upward.%d.pipe", process_id);

    process_downward_pipes[process_id] = fopen(process_downward_pipe_name, "w");
    process_upward_pipes[process_id] = fopen(process_upward_pipe_name, "r");

<<<<<<< HEAD
    assert(process_downward_pipes[descriptor]);
    assert(process_upward_pipes[descriptor]);
    fprintf(stderr, "DRIVER SUPERVISOR CLIENT: successfully opened pipes of algo \"%s\" with id %d \n", algo_name, descriptor);
=======
    trace("successfully opened pipes of process %d\n", process_id);
>>>>>>> 4b54911449a8d29736c62151628488d705380a86

    // Set auto flush
    setvbuf(process_downward_pipes[process_id], NULL, _IONBF, 0);
    
<<<<<<< HEAD
    return descriptor;
}

static int read_status() {
    int status;
    scanf(" %d", &status);
    fprintf(stderr, "DRIVER SUPERVISOR CLIENT: Status of request: %d\n", status);    
    return status;
}

int process_status(int algorithm_id) {
    fprintf(stderr, "DRIVER SUPERVISOR CLIENT: Requesting status of algo with id: %d...\n", algorithm_id);
    printf("process_status %d\n", algorithm_id);
=======
    return status;
}

int process_status(int process_id) {
    trace("Requesting status of process with id: %d...\n", process_id);
    fprintf(control_request_pipe, "process_status %d\n", process_id);
>>>>>>> 4b54911449a8d29736c62151628488d705380a86
    fflush(control_request_pipe);
    return read_status();
}

<<<<<<< HEAD
int process_kill(int algorithm_id) {
    fprintf(stderr, "DRIVER SUPERVISOR CLIENT: Killing algorithm with id: %d...\n", algorithm_id);
    printf("process_kill %d\n", algorithm_id);
=======
int process_stop(int process_id) {
    trace("Killing process with id: %d...\n", process_id);
    fprintf(control_request_pipe, "process_stop %d\n", process_id);
>>>>>>> 4b54911449a8d29736c62151628488d705380a86
    fflush(control_request_pipe);
    return read_status();
}

int read_file_open(const char *file_name) {
    
    // Open file for reading
<<<<<<< HEAD
    fprintf(stderr, "DRIVER SUPERVISOR CLIENT: Opening file with name: \"%s\"...\n", file_name);    
    printf("read_file_open %s\n", file_name);
=======
    trace("Opening file with name: \"%s\"...\n", file_name);    
    fprintf(control_request_pipe, "read_file_open %s\n", file_name);
>>>>>>> 4b54911449a8d29736c62151628488d705380a86
    fflush(control_request_pipe);
    int descriptor;
    scanf(" %d", &descriptor);
    

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

<<<<<<< HEAD
        fprintf(stderr, "DRIVER SUPERVISOR CLIENT: Closing pipe with id %d\n", id);
        printf("read_file_close %d\n", id);
=======
        trace("Closing pipe with id %d\n", id);
        fprintf(control_request_pipe, "read_file_close %d\n", id);
>>>>>>> 4b54911449a8d29736c62151628488d705380a86
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
}

