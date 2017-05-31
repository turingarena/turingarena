#include <cstdio>

void driver_init();

void* algorithm_create_process(const char *algo_name);

int process_start(void *handle);
int process_status(void *handle);
int process_stop(void *handle);

FILE *process_upward_pipe(void *handle);
FILE *process_downward_pipe(void *handle);