int algorithm_start(const char *algo_name);

int algorithm_status(int id);
int algorithm_kill(int id);

FILE *algorithm_input_pipe(int id);
FILE *algorithm_output_pipe(int id);


int read_file_open(const char *file_name);
FILE *read_file_pipe(int id);
int read_file_close(int id);


int write_file_open(const char *file_name);
FILE *write_file_pipe(int id);
int write_flie_close(int id);
