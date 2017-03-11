#include <stdlib.h>
#include <stdio.h>

#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <errno.h>
#include <string.h>

#include <cassert>

#include <string>
using namespace std;


#define DEBUG(...) fprintf(stderr, __VA_ARGS__)

void read_from_pipe (int file)
 {
   FILE *stream;
   int c;
   stream = fdopen (file, "r");
   while ((c = fgetc (stream)) != EOF)
     putchar (c);
   fclose (stream);
 }

void make_algorithm_pipes(int index) {

    // Generate file descriptor names
    char algorithm_output_pipe_name[200];
    sprintf(algorithm_output_pipe_name, "driver_sandbox/algorithm_output.%d.pipe", index);

    char algorithm_input_pipe_name[200];
    sprintf(algorithm_input_pipe_name, "driver_sandbox/algorithm_input.%d.pipe", index);

    mkfifo(algorithm_output_pipe_name, 0666);
    mkfifo(algorithm_input_pipe_name, 0666);
}

FILE* open_supervisor_writeto(int index) {
    char algorithm_input_pipe_name[200];
    sprintf(algorithm_input_pipe_name, "driver_sandbox/algorithm_input.%d.pipe", index);
    return fopen(algorithm_input_pipe_name, "w");
}

FILE* open_supervisor_readfrom(int index) {
    char algorithm_output_pipe_name[200];
    sprintf(algorithm_output_pipe_name, "driver_sandbox/algorithm_output.%d.pipe", index);
    return fopen(algorithm_output_pipe_name, "r");
}


FILE* open_algorithm_writeto(int index) {
    char algorithm_output_pipe_name[200];
    sprintf(algorithm_output_pipe_name, "algorithm_output.%d.pipe", index);
    DEBUG("Opening algorithm write pipe\n");
    FILE *f = fopen(algorithm_output_pipe_name, "w");
    assert(f);
    return f;
}

FILE* open_algorithm_readfrom(int index) {
    char algorithm_input_pipe_name[200];
    sprintf(algorithm_input_pipe_name, "algorithm_input.%d.pipe", index);
    DEBUG("Opening algorithm read pipe\n");    
    FILE *f = fopen(algorithm_input_pipe_name, "r");
    assert(f);
    return f;
}

static FILE *algorithm_input_pipes[2000];
static FILE *algorithm_output_pipes[2000];
static pid_t algorithm_pids[2000];

static int next_algorithm_index = 1;
static int next_file_index = 1;

void fork_algorithm(const char *algorithm_name, int index) { // index > 0!!!
    make_algorithm_pipes(index); // Make data/control file descriptors

    pid_t pid = fork();
    
    if (pid == 0) { /* child */
        chdir("driver_sandbox");    
        
        dup2(fileno(open_algorithm_writeto(index)), STDOUT_FILENO);
        dup2(fileno(open_algorithm_readfrom(index)), STDIN_FILENO);

        char executable_path[300];
        sprintf(executable_path, "../algorithms/%s/algorithm", algorithm_name);

        int r = execl(executable_path, "algorithm", (char *)0);
        if (r == -1) {
            fprintf(stderr, "Error while executing algorithm:\n\tr = %d   errno = %d\n",r,errno);
        }
        exit(0);
    }

    if (pid > 0) {
        algorithm_pids[index] = pid;
    }

    algorithm_input_pipes[index] = open_supervisor_readfrom(index);
    algorithm_output_pipes[index] = open_supervisor_writeto(index);
    setvbuf(algorithm_output_pipes[index], NULL, _IONBF, 0);
}

FILE *driver_control_output;
FILE *driver_control_input;

void fork_driver() {

    DEBUG("Creating driver pipes...\n");    
    make_algorithm_pipes(0); // Make control file descriptors

    pid_t pid = fork();
    
    if (pid == 0) { /* child */
        chdir("driver_sandbox");
        dup2(fileno(open_algorithm_writeto(0)), STDOUT_FILENO);
        dup2(fileno(open_algorithm_readfrom(0)), STDIN_FILENO);

        DEBUG("Finished redirect stdin/out\n");   

        DEBUG("Driver changed directory to driver_sandbox\n");     

        int r = execl("../driver/driver", "driver", (char *)0);
        if (r == -1) {
            fprintf(stderr, "Error while executing algorithm:\n\tr = %d   errno = %d\n",r,errno);
        }
        exit(0);
    }

    driver_control_input = open_supervisor_readfrom(0);
    driver_control_output = open_supervisor_writeto(0);
    setvbuf(driver_control_output, NULL, _IONBF, 0);

    DEBUG("Driver started.\n");    
}




int on_algorithm_start(const char *algo_name) {
    int current_algorithm_index = next_algorithm_index++;
    fork_algorithm(algo_name, current_algorithm_index);
    return current_algorithm_index;
}
int on_algorithm_status(int id) {
    return 0;
}


int on_algorithm_kill(int id) {
    if (algorithm_pids[id] != 0) {
        kill(algorithm_pids[id], SIGKILL);
        fprintf(stderr, "Killed process with pid %d\n", algorithm_pids[id]);
        algorithm_pids[id] = 0;
        return 0;
    }
    return -1;
}

int on_read_file_open(const char *file_name) {

    int id = next_file_index++;

    char read_file_name_source[200];
    sprintf(read_file_name_source, "../read_files/%s/data.txt", file_name);

    char read_file_name_dest[200];
    sprintf(read_file_name_dest, "driver_sandbox/read_file.%d.txt", id);


    symlink(read_file_name_source, read_file_name_dest);

    return id;
}

int on_read_file_close(int id) {
    char read_file_name_dest[200];
    sprintf(read_file_name_dest, "driver_sandbox/read_file.%d.pipe", id);
    return unlink(read_file_name_dest);
}



void ctrl_loop() {

#define CASE(s) if (!strcmp(command, s))

    while (1) {
        //for (int i = 0; i < 2; i++) {
        //fprintf(stderr, "Waiting...\n");

        char command[500] = { 0 };
        char name[500] = { 0 };
        int proc_id;

        fprintf(stderr, "SUPERVISOR: waiting for commands...\n");

        fscanf(driver_control_input, " %500s", command);

        if (feof(driver_control_input)) break;

        fprintf(stderr, "SUPERVISOR: received command \"%s\"\n", command);

        CASE("algorithm_start") {
            fscanf(driver_control_input, "%s", name);
            int id = on_algorithm_start(name);
            fprintf(driver_control_output, "%d\n", id);
            fprintf(stderr, "SUPERVISOR: Started process\n");
        }
        CASE("algorithm_status") {
            fscanf(driver_control_input, "%d", &proc_id);
            fprintf(driver_control_output, "%d\n", on_algorithm_status(proc_id));
            fprintf(stderr, "SUPERVISOR: Requested status\n");            
        }
        CASE("algorithm_kill") {
            fscanf(driver_control_input, "%d", &proc_id);
            fprintf(driver_control_output, "%d\n", on_algorithm_kill(proc_id));
            fprintf(stderr, "SUPERVISOR: Killed process with id %d\n", proc_id);
        }
        CASE("read_file_open") {
            fscanf(driver_control_input, "%s", name);
            int id = on_read_file_open(name);
            fprintf(driver_control_output, "%d\n", id);
            fprintf(stderr, "SUPERVISOR: Opened file\n");
        }
        CASE("read_file_close") {
            int file_id;
            fscanf(driver_control_input, "%d", &file_id);
            fprintf(driver_control_output, "%d\n", on_read_file_close(file_id));
            fprintf(stderr, "SUPERVISOR: Closed file %d\n", file_id);
        }
    }
}



int main(int argc, char** argv) {

    DEBUG("Supervisor started\n");

    fork_driver();

    DEBUG("Starting control loop...\n");

    ctrl_loop();
}