#include "module.h"
#include <cstdlib>
#include <cstdio>

const int N_MAX = 1000;

int main() {
    int A = rand() % N_MAX;
    int B = rand() % N_MAX;

    void* solution = algorithm_create_process("solution");
    process_start(solution);

    fprintf(process_downward_pipe(solution), "%d %d\n", A, B);
    fflush(process_downward_pipe(solution));

    int sum;
    fscanf(process_downward_pipe(solution), "%d", sum);
    process_stop(solution);

    if(sum == A+B) {
        printf("correct\n");
    } else {
        printf("not correct\n");
    }

    return 0;
}
