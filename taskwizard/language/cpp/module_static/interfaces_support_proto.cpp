#include <algorithm>
#include <stdarg.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>

using namespace std;

// Recursive callback handler definition
typedef bool (*callbacks_handler_func)(void *handler, char *signature);

// Corutine definition
typedef void (*corutine_func)(void *, uint32_t);

struct interface_common_data {
    pair<corutine_func, int> state;
    callbacks_handler_func default_callback_handler;
};



struct proc_handle_structure {
    int proc_id;
    FILE *upward_pipe;
    FILE *downward_pipe;
    interface_common_data *common_data;
    void *interface_data;
};

void __driver_init(void *handle) {
    proc_handle_structure *handle_struct = (proc_handle_structure*) handle;
    handle_struct->common_data = new interface_common_data();
    handle_struct->common_data->state = make_pair((corutine_func)NULL, NULL);
    handle_struct->common_data->default_callback_handler = NULL;
}


void __driver_send(void *handle, const char* format, ...) {
    proc_handle_structure *handle_struct = (proc_handle_structure*) handle;

    va_list arg;
    int done;

    va_start (arg, format);
    done = vfprintf(handle_struct->downward_pipe, format, arg);
    va_end (arg);
    putc_unlocked(' ', handle_struct->downward_pipe);
}

void __driver_end_batch(void *handle) {
    proc_handle_structure *handle_struct = (proc_handle_structure*) handle;    
    putc_unlocked('\n', handle_struct->downward_pipe);
    fflush(stdout);
}

void __driver_call(void *handle, const char* format, ...) {
    proc_handle_structure *handle_struct = (proc_handle_structure*) handle;

    __driver_end_batch(handle); 
    fflush(stdout);
    va_list arg;
    int done;
    
    va_start (arg, format);
    done = vfscanf(handle_struct->upward_pipe, format, arg);
    va_end (arg);
}

void __driver_call_recursive(void *handle, const char* format, ...) {
    proc_handle_structure *handle_struct = (proc_handle_structure*) handle;

    __driver_end_batch(handle); 
    char buffer[256] = {0};
    do {
        fflush(stdout);
        fscanf(handle_struct->upward_pipe, "%255s", buffer);  
    }
    while (handle_struct->common_data->default_callback_handler(handle, buffer));

    va_list arg;
    int done;
    
    va_start (arg, format);
    done = vfscanf(handle_struct->upward_pipe, format, arg);
    va_end (arg);
}

void __driver_throw(const char* str) {
    fprintf(stderr, "ERROR WHILE PROCESSING: %s\n", str);
    exit(1);
}

void __driver_call_void(void *handle) {
    proc_handle_structure *handle_struct = (proc_handle_structure*) handle;
    __driver_end_batch(handle); 
    fflush(stdout);
    return;
}