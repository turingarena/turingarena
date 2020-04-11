#include <cstdio>

volatile int x[40000000];

int main() {
//#ifdef EVAL
//    freopen("input.txt", "r", stdin);
//    freopen("output.txt", "w", stdout);
//#endif
    int N, max;
    scanf("%d", &N);

    for (long long i=0; i < 40000000; i++) {
        x[i] = 1;
    }

    for (long long i=0; i < 10000000; i++) {
        scanf("");
    }

    for (int i=0; i<N; i++) {
        int x;
        scanf("%d", &x);
        if (i == 0 || x > max)
            max = x;
    }
    printf("%d\n", max);
}
