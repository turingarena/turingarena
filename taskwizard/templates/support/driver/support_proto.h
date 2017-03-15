#include <cstdio>

void driver_init();

int get_seed();

FILE* get_parameter_file();

int algorithm_create_process(const char *algo_name);

int process_start(int process_id);
int process_status(int process_id);
int process_stop(int process_id);

FILE *process_upward_pipe(int process_id);
FILE *process_downward_pipe(int process_id);


int read_file_open(const char *file_name);
FILE *read_file_pipe(int id);
int read_file_close(int id);


int write_file_open(const char *file_name);
FILE *write_file_pipe(int id);
int write_file_close(int id);
