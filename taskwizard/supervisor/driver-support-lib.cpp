#include <stdio.h>

#include <sys/types.h>
#include <sys/stat.h>

#include <stdarg.h>


FILE *inpipes[2000];
FILE *outpipes[2000];

static int current_process;

FILE *get_input_pipe() {
    return inpipes[current_process];
}

FILE *get_output_pipe() {
    return outpipes[current_process];
}


int task_start() {
    printf("task_start\n");
    fprintf(stderr, "DRIVER: Starting task...\n");
    int descriptor;
    scanf("%d", &descriptor);
    fprintf(stderr, "DRIVER: Received confirm, task id: %d\n", descriptor);
    fprintf(stderr, "Desc %d\n", descriptor);
    fflush(stderr);

    char read_pipe_name[200];
    sprintf(read_pipe_name, "wfdesc%d", descriptor);

    char write_pipe_name[200];
    sprintf(write_pipe_name, "rfdesc%d", descriptor);

    inpipes[descriptor] = fopen(read_pipe_name, "r");
    outpipes[descriptor] = fopen(write_pipe_name, "w");

    setvbuf(outpipes[descriptor], NULL, _IONBF, 0);
    
    return descriptor;
}

int task_status() {
    printf("task_status %d\n", current_process);
    int status;
    scanf(" %d", &status);
    return status;
}

void task_kill() {
    printf("task_kill %d\n", current_process);
    int status;
    scanf(" %d", &status);
}

void task_set_current(int id) {
    current_process = id;
}

int task_get_current() {
    return current_process;
}

void init_communication() {
    printf("init_communication\n");
    int status;
    scanf(" %d", &status);
}

/*int main() {


    init_communication();
    int taskid = task_start();
    task_set_current(taskid);

    int taskstatus = task_status();

    task_kill();
}*/