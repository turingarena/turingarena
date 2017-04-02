#include <stdlib.h>
#include <stdio.h>
#include <stdarg.h>
#include <vector>
#include <algorithm>
#include <stdint.h>
#include <stack>

using namespace std;

/////////////////////////// LIMITS ///////////////////////////
#define MINN 0
#define MAXN 1000

#define MINM 0
#define MAXM 1000

#define MINAi -0xFFFFFFFF
#define MAXAi 0x7FFFFFFF
/////////////////////////// END LIMITS ///////////////////////////

/////////////////////////// GLOBALS ///////////////////////////
struct alien_globals {
/*GLOBALS GENERATED*/
    int N;
    int M;
    int* A;
    int** B; // or int B[MAXN][MAXM];
    int X;
    int Y;
/*GLOBALS GENERATED END*/
};
/////////////////////////// END GLOBALS ///////////////////////////


/////////////////////////// INTERNALS ///////////////////////////
struct alien_internals {
    int N;
    int Xi;
    int Yi;
    int result;
    int x;
    int y;
    int *C;
};
/////////////////////////// END INTERNALS ///////////////////////////


/////////////////////////// ACTIONS ///////////////////////////
enum ALIEN_ACTIONS {
    INIT_CORUTINE,
    FINALIZE_CORUTINE,
    CALL_UPDATE,
    CALL_QUERY,
    CALL_FILL,
    CALL_FIND_CENTRE,
    FLUSH
};
/////////////////////////// ENDACTIONS ///////////////////////////

// Corutine definition
typedef void (*corutine_func)(void *, ALIEN_ACTIONS);

// Recursive callback handler definition
typedef bool (*callbacks_handler_func)(void *handler, char *signature);


// Corutine prototypes
void flow_alien_corutine(void *handle, ALIEN_ACTIONS action);
void flow_alien_examine_corutine(void *handle, ALIEN_ACTIONS action);


// Driver callback functions
int alien_on_examine(void *handle, int x, int y);

// Support callback functions
void __callback_alien_examine(void *handle);


/////////////////////////// GLOBALS INITIALIZATION ROUTINE ///////////////////////////
void __initialize_globals(alien_globals **globals) {
    *globals = (alien_globals*)calloc(1, sizeof(alien_globals));
    new (*globals) alien_globals();


    (*globals)->A = (int*)calloc(MAXN, sizeof(int));
    
    (*globals)->B = (int**)calloc(MAXN, sizeof(int*));
    for (int i = 0; i < MAXN; i++) {
        (*globals)->B[i] = (int*)calloc(MAXM, sizeof(int));
    }
}
/////////////////////////// END GLOBALS INITIALIZATION ROUTINE ///////////////////////////







// Corutine helper macros
#if 1 // Fix highlight error
#define BEGIN_CORUTINE switch (((alien_proc_handle*)handle)->state.second) { case 0: RETURN_CONTROL
#endif

#define END_CORUTINE RETURN_CONTROL; } __driver_throw("No more commands can be executed!\n")
#define RETURN_CONTROL ((alien_proc_handle*)handle)->state.second = __LINE__; return; case __LINE__:

/////////////////////////// PROCESS INTERNAL STRUCTURE ///////////////////////////
struct alien_proc_handle {
    FILE *downward_pipe;
    FILE *upward_pipe;
    alien_internals *internals;
    pair<corutine_func, int> state;
    alien_globals* globals;
    callbacks_handler_func default_callback_handler;
};
/////////////////////////// END PROCESS INTERNAL STRUCTURE ///////////////////////////



/////////////////////////// DRIVER COMMON ROUTINES ///////////////////////////
void __driver_send(void *handle, const char* format, ...) {
    va_list arg;
    int done;

    va_start (arg, format);
    done = vfprintf(((alien_proc_handle*)handle)->downward_pipe, format, arg);
    va_end (arg);
    putc_unlocked(' ', ((alien_proc_handle*)handle)->downward_pipe);
}

void __driver_end_batch(void *handle) {
    putc_unlocked('\n', ((alien_proc_handle*)handle)->downward_pipe);
    fflush(stdout);
}

void __driver_call(void *handle, const char* format, ...) {
    
    __driver_end_batch(handle); 
    fflush(stdout);
    va_list arg;
    int done;
    
    va_start (arg, format);
    done = vfscanf(((alien_proc_handle*)handle)->upward_pipe, format, arg);
    va_end (arg);
}

void __driver_call_recursive(void *handle, const char* format, ...) {

    __driver_end_batch(handle); 
    char buffer[256] = {0};
    do {
        fflush(stdout);
        fscanf(((alien_proc_handle*)handle)->upward_pipe, "%255s", buffer);  
    }
    while (((alien_proc_handle*)handle)->default_callback_handler(handle, buffer));

    va_list arg;
    int done;
    
    va_start (arg, format);
    done = vfscanf(((alien_proc_handle*)handle)->upward_pipe, format, arg);
    va_end (arg);
}

void __driver_throw(const char* str) {
    fprintf(stderr, "ERROR WHILE PROCESSING: %s\n", str);
    exit(1);
}

void __driver_call_void(void *handle) {
    __driver_end_batch(handle); 
    fflush(stdout);
    return;
}

/*void __driver_recv_parameters_array(const char* format, int size, void* array) {

}*/

void __driver_prefix_call(void *handle, const char *pref) {
    __driver_send(handle, "%s", pref);
}

void __driver_recv(void *handle, const char* format, ...) {

    va_list arg;
    int done;
    
    va_start (arg, format);
    done = vfscanf(((alien_proc_handle*)handle)->upward_pipe, format, arg);
    va_end (arg);
}
/////////////////////////// END DRIVER COMMON ROUTINES ///////////////////////////


/////////////////////////// FLOW CORUTINES ///////////////////////////

void flow_alien_corutine(void *handle, ALIEN_ACTIONS action) {

    BEGIN_CORUTINE;
            __driver_send(handle, "%d", ((alien_proc_handle*)handle)->globals->N);
            __driver_send(handle, "%d", ((alien_proc_handle*)handle)->globals->M);
            __driver_end_batch(handle);

            //find_centre();
            switch(action) {
                case CALL_FIND_CENTRE:
                    __driver_send(handle, "%d %d %d", 
                                ((alien_proc_handle*)handle)->internals->N,
                                ((alien_proc_handle*)handle)->internals->Xi,
                                ((alien_proc_handle*)handle)->internals->Yi
                                );       
    //                __driver_call_void();
                    __driver_call_recursive(handle, "%d", &(((alien_proc_handle*)handle)->internals->result));

                break;
                default:
                    __driver_throw("Only a call to find_centre is expected\n");
            }


        RETURN_CONTROL;

            for (int i = 0; i < ((alien_proc_handle*)handle)->globals->N; i++)
                __driver_send(handle, "%d", ((alien_proc_handle*)handle)->globals->A[i]);
            __driver_end_batch(handle);   
            
            for (int i = 0; i < ((alien_proc_handle*)handle)->globals->N; i++) {
                for (int j = 0; j < ((alien_proc_handle*)handle)->globals->M; j++)
                    __driver_send(handle, "%d", ((alien_proc_handle*)handle)->globals->B[i][j]);
                __driver_end_batch(handle);
            }

            switch(action) {
                case CALL_FIND_CENTRE:
                    __driver_send(handle, "%d %d %d", 
                                ((alien_proc_handle*)handle)->internals->N,
                                ((alien_proc_handle*)handle)->internals->Xi,
                                ((alien_proc_handle*)handle)->internals->Yi
                                );      
    //                __driver_call_void();
                    __driver_call_recursive(handle, "%d", &(((alien_proc_handle*)handle)->internals->result));
                break;
                default:
                    __driver_throw("Only a call to find_centre is expected\n");
            }
            
        RETURN_CONTROL;
            switch(action) {
                case CALL_UPDATE:
                    __driver_prefix_call(handle, "u");
                    __driver_call_recursive(handle, "%d", &(((alien_proc_handle*)handle)->internals->result));
                break;

                case CALL_QUERY:
                    __driver_prefix_call(handle, "q");            
                    __driver_call_recursive(handle, "%d", &(((alien_proc_handle*)handle)->internals->result));

                break;

                case CALL_FILL:
                    __driver_prefix_call(handle, "f");     
                    __driver_call_recursive(handle, "%d", &(((alien_proc_handle*)handle)->internals->result));


                    if (!((alien_proc_handle*)handle)->internals->C) {
                        __driver_throw("Error array C not initialized!!\n");
                    }
                    for (int i = 0; i < ((alien_proc_handle*)handle)->internals->result; i++) {
                        __driver_recv(handle, "%d", &((alien_proc_handle*)handle)->internals->C[i]);
                    }
                break;

                default:
                    __driver_throw("Unexpected action\n");
            }
            for (int i = 0; i < ((alien_proc_handle*)handle)->globals->N; i++)        
                __driver_recv(handle, "%d", &((alien_proc_handle*)handle)->globals->A[i]);

            for (int i = 0; i < ((alien_proc_handle*)handle)->globals->N; i++)
                for (int j = 0; j < ((alien_proc_handle*)handle)->globals->M; j++)
                    __driver_recv(handle, "%d", &((alien_proc_handle*)handle)->globals->B);
    END_CORUTINE;

}



void flow_alien_examine_corutine(void *handle, ALIEN_ACTIONS action) {

    BEGIN_CORUTINE;

            for (;;) {
                switch (action) {
                    case CALL_QUERY:
                        __driver_prefix_call(handle, "q");
                        __driver_call_recursive(handle, "%d", &((alien_proc_handle*)handle)->internals->result);
                    break;
                    case CALL_UPDATE:
                        __driver_prefix_call(handle, "#"); // Exit cycle                    
                        __driver_send(handle, "%d %d", ((alien_proc_handle*)handle)->globals->X, ((alien_proc_handle*)handle)->globals->Y);
                        __driver_call(handle, "%d", &((alien_proc_handle*)handle)->internals->result);
                        goto exit_loop;
                    default:
                        __driver_throw("Only a call to query is expected!\n"); 
                }
                
        RETURN_CONTROL;
                switch (action) {
                    case CALL_UPDATE:
                    __driver_prefix_call(handle, "u");
                    __driver_call(handle, "%d", &((alien_proc_handle*)handle)->internals->result);
                    break;
                    default:
                    __driver_throw("Only a call to update is expected!\n");
                }
        RETURN_CONTROL;
            }
            exit_loop:
        RETURN_CONTROL;
            switch (action) {
                case FINALIZE_CORUTINE: {
                    __driver_send(handle, "%d", ((alien_proc_handle*)handle)->internals->result);
                    __driver_end_batch(handle);                            
                }
                break;
                default:
                    __driver_throw("Function should now return\n");
            }
    END_CORUTINE;
}

/////////////////////////// END FLOW CORUTINES ///////////////////////////

// Helper function to continue corutine execution
void execute_top_corutine(void *handle, ALIEN_ACTIONS action) {
    ((alien_proc_handle*)handle)->state.first(handle, action);
}

/////////////////////////// GLOBAL CALLBACK HANDLER (FIXME) ///////////////////////////
bool alien_handle_function_callbacks(void *handle, char *signature) {
    fprintf(stderr, "Waiting for callbacks with sig '%s'\n", signature);
    switch (signature[0]) {
            case 'r':
                return false;
            break;
            case 'e':
                __callback_alien_examine(handle);
                break;
        }
    return true;
}
/////////////////////////// END GLOBAL CALLBACK HANDLER (FIXME) ///////////////////////////





/////////////////////////// EXPORTED FUNCTIONS  ///////////////////////////

alien_globals* alien_get_globals(void *handle) {
    if (!((alien_proc_handle*)handle)->globals) {
        __initialize_globals(&((alien_proc_handle*)handle)->globals);
    }
    return ((alien_proc_handle*)handle)->globals;
}


int alien_call_query(void *handle) {
    execute_top_corutine(handle, CALL_QUERY);
    return ((alien_proc_handle*)handle)->internals->result;
}

int alien_call_update(void *handle) {
    execute_top_corutine(handle, CALL_UPDATE);
    return ((alien_proc_handle*)handle)->internals->result;
}


int alien_call_fill(void *handle, int C[]) {

    ((alien_proc_handle*)handle)->internals->C = C;
    execute_top_corutine(handle, CALL_FILL);

    
    return ((alien_proc_handle*)handle)->internals->result;
}

int alien_call_find_centre(void *handle, int N, int Xi, int Yi) {
    ((alien_proc_handle*)handle)->internals->N = N;
    ((alien_proc_handle*)handle)->internals->Xi = Xi;
    ((alien_proc_handle*)handle)->internals->Yi = Yi;
    execute_top_corutine(handle, CALL_FIND_CENTRE);
    return ((alien_proc_handle*)handle)->internals->result;
}
/////////////////////////// END EXPORTED FUNCTIONS ///////////////////////////


/////////////////////////// INTERNAL CALLBACKS ///////////////////////////
void __callback_alien_examine(void *handle) {
    
    // Create new stack frame
    alien_internals *old_stackframe = ((alien_proc_handle*)handle)->internals;
    alien_internals new_stackframe = {0};
    ((alien_proc_handle*)handle)->internals = &new_stackframe;
    pair<corutine_func, int> old_programcounter = ((alien_proc_handle*)handle)->state;
    ((alien_proc_handle*)handle)->state = make_pair(flow_alien_examine_corutine, 0);

    __driver_recv(handle, "%d%d", &((alien_proc_handle*)handle)->internals->x, &((alien_proc_handle*)handle)->internals->y);

    execute_top_corutine(handle, INIT_CORUTINE);

    // Call driver function
    ((alien_proc_handle*)handle)->internals->result = alien_on_examine(handle, ((alien_proc_handle*)handle)->internals->x, ((alien_proc_handle*)handle)->internals->y);
    execute_top_corutine(handle, FINALIZE_CORUTINE);

    // Restore previous stack frame
    ((alien_proc_handle*)handle)->state = old_programcounter;
    ((alien_proc_handle*)handle)->internals = old_stackframe;
}
/////////////////////////// END INTERNAL CALLBACKS ///////////////////////////



/////////////////////////// TEST MAIN (FIXME) ///////////////////////////
void driver_main(void *handle);
int main(){
    alien_proc_handle p = {0}; 
    p.downward_pipe = stdout;
    p.upward_pipe = stdin;
    p.default_callback_handler = alien_handle_function_callbacks;


    alien_internals new_stackframe = {0};
    p.internals = &new_stackframe;
    p.state = make_pair(flow_alien_corutine, 0);

    execute_top_corutine(&p, INIT_CORUTINE);
    driver_main(&p);
}
/////////////////////////// END TEST MAIN (FIXME) ///////////////////////////


