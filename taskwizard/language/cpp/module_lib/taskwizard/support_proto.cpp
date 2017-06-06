#include <bits/stdc++.h>
#include "support_proto.h"

#define MAX_LEN 2048

#define trace(...) do { \
    fprintf(stderr, "supervisor client: "); \
    fprintf(stderr, __VA_ARGS__); \
  } while(0);

struct proc_handle_structure {
    int process_id;
    FILE *upward_pipe;
    FILE *downward_pipe;
};

static const char *sandbox_dir_env = "TASKWIZARD_SANDBOX_DIR";

static int inited = 0;
static char *sandbox_dir;

static FILE *control_request_pipe;
static FILE *control_response_pipe;

FILE *process_upward_pipe(void *handle) {
    proc_handle_structure *handle_struct = (proc_handle_structure*) handle;
    return handle_struct->upward_pipe;
}

FILE *process_downward_pipe(void *handle) {
    proc_handle_structure *handle_struct = (proc_handle_structure*) handle;
    return handle_struct->downward_pipe;
}

int driver_init() {
    sandbox_dir = getenv(sandbox_dir_env);
    if(!sandbox_dir) {
        trace("environment variable '%s' not set, make sure to user 'taskwizard run' to run this program\n", sandbox_dir_env);
        goto err;
    }

    char filename[MAX_LEN];
    int len;

    trace("Opening request pipe...\n");
    len = snprintf(filename, MAX_LEN, "%s/control_request.pipe", sandbox_dir);
    if(len < 0 || len >= MAX_LEN) {
        trace("unable to create control request pipe path\n");
        goto err;
    }
    control_request_pipe = fopen(filename, "w");
    if(!control_request_pipe) {
        trace("Unable to open request pipe: %s\n", strerror(errno));
        goto err;
    }
    trace("Request pipe opened.");

    trace("Opening response pipe...\n");
    len = snprintf(filename, MAX_LEN, "%s/control_response.pipe", sandbox_dir);
    if(len < 0 || len >= MAX_LEN) {
        trace("unable to create control request pipe path\n");
        goto err;
    }
    control_response_pipe = fopen(filename, "r");
    if(!control_response_pipe) {
        trace("Unable to open response pipe: %s\n", strerror(errno));
        goto err;
    }
    trace("Response pipe opened.");

    inited = 1;
    return 1;

    err:
    return 0;
}

static void check_inited() {
    if(inited) return;

    trace("method called but not initialized, terminating...\n")
    exit(EXIT_FAILURE);
}

void* algorithm_create_process(const char *algo_name) {
    check_inited();

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
    check_inited();

    proc_handle_structure *handle_struct = (proc_handle_structure*) handle;

    trace("Starting process with id: %d...\n", handle_struct->process_id);
    fprintf(control_request_pipe, "process_start %d\n", handle_struct->process_id);
    fflush(control_request_pipe);
    
    int status = read_status();

    char filename[MAX_LEN];
    int len;

    len = snprintf(filename, MAX_LEN, "%s/process_downward.%d.pipe", sandbox_dir, handle_struct->process_id);
    if(len < 0 || len >= MAX_LEN) {
        trace("unable to create process downward pipe path\n");
        goto err;
    }
    handle_struct->downward_pipe = fopen(filename, "w");

    len = snprintf(filename, MAX_LEN, "%s/process_upward.%d.pipe", sandbox_dir, handle_struct->process_id);
    if(len < 0 || len >= MAX_LEN) {
        trace("unable to create process upward pipe path\n");
        goto err;
    }
    handle_struct->upward_pipe = fopen(filename, "r");

    trace("successfully opened pipes of process %d\n", handle_struct->process_id);

    // Set auto flush
    setvbuf(handle_struct->downward_pipe, NULL, _IONBF, 0);
    
    return status;

    err:
    return -1;
}

int process_status(void *handle) {
    check_inited();

    proc_handle_structure *handle_struct = (proc_handle_structure*) handle;
    trace("Requesting status of process with id: %d...\n", handle_struct->process_id);
    fprintf(control_request_pipe, "process_status %d\n", handle_struct->process_id);
    fflush(control_request_pipe);
    return read_status();
}

int process_stop(void *handle) {
    check_inited();

    proc_handle_structure *handle_struct = (proc_handle_structure*) handle;
    trace("Killing process with id: %d...\n", handle_struct->process_id);
    fprintf(control_request_pipe, "process_stop %d\n", handle_struct->process_id);
    fflush(control_request_pipe);
    return read_status();
}
