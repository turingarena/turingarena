#include <cstdio>

void driver_init();

int get_seed();

FILE* get_parameter_file();

void* algorithm_create_process(const char *algo_name);

int process_start(void *handle);
int process_status(void *handle);
int process_stop(void *handle);

FILE *process_upward_pipe(void *handle);
FILE *process_downward_pipe(void *handle);

/*
int read_file_open(const char *file_name);
FILE *read_file_pipe(int id);
int read_file_close(int id);


int write_file_open(const char *file_name);
FILE *write_file_pipe(int id);
int write_file_close(int id);
*/