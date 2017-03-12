#include <bits/stdc++.h>

FILE *algorithm_upward_pipes[2000];
FILE *algorithm_downward_pipes[2000];

FILE *read_file_pipes[2000];
FILE *write_file_pipes[2000];

FILE *algorithm_upward_pipe(int id) {
    return algorithm_upward_pipes[id];
}

FILE *algorithm_downward_pipe(int id) {
    return algorithm_downward_pipes[id];
}

int algorithm_start(const char *algo_name) {
    // Start new algorithm    
    printf("algorithm_start %s\n", algo_name);
    fflush(stdout);
    int descriptor;
    scanf("%d", &descriptor);

    // Generate file descriptor names
    char algorithm_downward_pipe_name[200];
    sprintf(algorithm_downward_pipe_name, "algorithm_downward.%d.pipe", descriptor);

    char algorithm_upward_pipe_name[200];
    sprintf(algorithm_upward_pipe_name, "algorithm_upward.%d.pipe", descriptor);

    // Open descriptors
    algorithm_downward_pipes[descriptor] = fopen(algorithm_downward_pipe_name, "w");
    algorithm_upward_pipes[descriptor] = fopen(algorithm_upward_pipe_name, "r");

    // Set auto flush
    setvbuf(algorithm_downward_pipes[descriptor], NULL, _IONBF, 0);
    
    return descriptor;
}

static int read_status() {
    int status;
    scanf(" %d", &status);
    return status;
}

int algorithm_status(int id) {
    printf("algorithm_status %d\n", id);
    fflush(stdout);
    return read_status();
}

int algorithm_kill(int id) {
    printf("algorithm_kill %d\n", id);
    fflush(stdout);
    return read_status();
}

int read_file_open(const char *file_name) {
    
    // Open file for reading
    
    printf("read_file_open %s\n", file_name);
    fflush(stdout);
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
    fprintf(stderr, "Requested id %d with pointer: %p\n",id, read_file_pipes[id]);
    return read_file_pipes[id];
}

int read_file_close(int id) {
    fclose(read_file_pipes[id]);
    read_file_pipes[id] = NULL;

    printf("read_file_close %d\n", id);
    fflush(stdout);
    int status;
    scanf(" %d", &status);

    return status;
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

