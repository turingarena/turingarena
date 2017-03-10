#include <stdio.h>

#include <sys/types.h>
#include <sys/stat.h>


static FILE *inpipes[2000];
static FILE *outpipes[2000];

static int current_task;


int task_start() {
    printf("task_start\n");
    int descriptor;
    scanf(" %d", &descriptor);
    fprintf(stderr, "Desc %d\n", descriptor);

    char read_pipe_name[200];
    sprintf(read_pipe_name, "wfdesc%d", descriptor);

    char write_pipe_name[200];
    sprintf(write_pipe_name, "rfdesc%d", descriptor);

    inpipes[descriptor] = fopen(read_pipe_name, "r");
    outpipes[descriptor] = fopen(write_pipe_name, "w");
    
    return descriptor;
}

void print_success() {
    char buff[50] = {0};
    fprintf(stderr, "pipe: %p\n", inpipes[1]);
    fscanf(inpipes[1], "%s", buff);
    //printf("Thedriverreceivedthisstringfromsubmission:%s\n", buff);
    fprintf(stderr, "Thedriverreceivedthisstringfromsubmission:%s\n", buff);
}

int task_status() {
    printf("task_status %d\n", current_task);
    int status;
    scanf(" %d", &status);
    return status;
}

void task_kill() {
    printf("task_kill %d\n", current_task);
    int status;
    scanf(" %d", &status);
}

void task_set_current(int id) {
    current_task = id;
}

int task_get_current() {
    return current_task;
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