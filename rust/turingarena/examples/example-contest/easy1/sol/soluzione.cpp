#include <cstdio>
int main() {
//#ifdef EVAL
//    freopen("input.txt", "r", stdin);
//    freopen("output.txt", "w", stdout);
//#endif
    int N, max;
    scanf("%d", &N);
    for (int i=0; i<N; i++) {
        int x;
        scanf("%d", &x);
        if (i == 0 || x > max)
            max = x;
    }
    printf("%d\n", max);
}
