#include <bits/stdc++.h>
#include "driver.h"

FILE *inpipes[2000];
FILE *outpipes[2000];

static int current_process;

FILE *get_input_pipe() {
    return inpipes[current_process];
}

FILE *get_output_pipe() {
    return outpipes[current_process];
}


int start_algorithm(const char *algo_name) {
    
    // Start new algorithm
    
    printf("start_algorithm %s\n", algo_name);
    int descriptor;
    scanf("%d", &descriptor);
    fflush(stderr);

    // Generate file descriptor names

    char read_pipe_name[200];
    sprintf(read_pipe_name, "wfdesc%d", descriptor);

    char write_pipe_name[200];
    sprintf(write_pipe_name, "rfdesc%d", descriptor);


    // Open descriptors
    inpipes[descriptor] = fopen(read_pipe_name, "r");
    outpipes[descriptor] = fopen(write_pipe_name, "w");

    // Set auto flush
    setvbuf(outpipes[descriptor], NULL, _IONBF, 0);
    
    return descriptor;
}

int algorithm_status() {
    printf("algorithm_status %d\n", current_process);
    int status;
    scanf(" %d", &status);
    return status;
}

int algorithm_kill() {
    printf("algorithm_kill %d\n", current_process);
    int status;
    scanf(" %d", &status);
}

void get_active_algorithm(int id) {
    current_process = id;
}

int set_active_algorithm() {
    return current_process;
}

void init_communication() {
    printf("init_communication\n");
    int status;
    scanf(" %d", &status);
}
