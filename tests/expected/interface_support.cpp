#include <cstdio>

extern int N;
extern int M;
extern int *A;
extern int S;

int solve(int N, int M);

int main() {
    scanf("%d%d", &N, &M);
    A = new int[N+1];
    for(int i = 1; i <= N; i++) {
        scanf("%d", &A[i]);
    }
    S = solve(N, M);
    printf("%d\n", S);
}
