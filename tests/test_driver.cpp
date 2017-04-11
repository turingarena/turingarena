#include "driver.h"

void evaluate() {
    exampleinterface solution;

    int N = 100;
    int M = 1000;

    solution.set_N(N);
    solution.set_M(M);

    solution.create_A();
    for(int i = 0; i < N; i++) {
        solution.set_A(i, 3);
    }

    int S = solution.call_solve(N, M);
}
