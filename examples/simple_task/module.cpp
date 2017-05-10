#include "module.h"

int main() {
    void* p = algorithm_create_process("solution");

    process_start(p);

    FILE* upward = process_upward_pipe(p);
    FILE* downward = process_downward_pipe(p);

    int N = 10;
    int M = 50;
    fprintf(downward, "%d %d\n", N, M)

    int S;
    fscanf(upward, "%d", &S);

    printf("%d\n", S);

    process_stop(p);
}
