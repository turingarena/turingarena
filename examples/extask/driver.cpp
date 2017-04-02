
#include <cstdlib>
#include <stdio.h>

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


const int N_MAX = 1000;


int alien_call_query(void *handle);
int alien_call_update(void *handle);
int alien_call_fill(void *handle, int C[]);
int alien_call_find_centre(void *handle, int N, int Xi, int Yi);

alien_globals* alien_get_globals(void *handle);



int alien_on_examine(void *handle, int x, int y) {
    fprintf(stderr, "Called examine with parameters: x: %d, y: %d\n", x, y);
    
    int qsum = 0;
    int usum = 0;
    while (qsum-usum < 100) {
        qsum += alien_call_query(handle);
        usum += alien_call_update(handle);
    }

    alien_get_globals(handle)->X = qsum;
    alien_get_globals(handle)->Y = usum;
    alien_call_update(handle);

    return x + y;
}


/*int on_alien_solution(int x, int y) {
  
}*/


int C[256];
void driver_main(void *handle) {

    alien_globals *globals = alien_get_globals(handle);

    globals->N = 25;
    globals->M = 17;


    for (int i = 0; i < 7; i++) {
        globals->B[i][i] = i;
    }
    alien_call_find_centre(handle, 5, 7, 9);
    alien_call_find_centre(handle, 5, 7, 9);
    
    int len = alien_call_update(handle);
    //len = alien_call_fill(handle, C);

    fprintf(stderr, "Returned array of length %d:\n", len);
    for (int i = 0; i < len; i++) {
        fprintf(stderr, "%d ", C[i]);
    }
    fprintf(stderr, "\n");
    fflush(stderr);

}

