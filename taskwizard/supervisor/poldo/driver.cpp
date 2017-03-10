#include <iostream>
#include <stdio.h>

using namespace std;




int task_start();
int task_status();
void task_kill();
void task_set_current(int id);
int task_get_current();
void print_success();


void driver_entry() {

    int proc = task_start();
    print_success();
    //task_status();
    //task_kill();
    //task_set_current(5);
    //task_kill();


}

int main() {
    setvbuf(stdout, NULL, _IONBF, 0);

    driver_entry();

}