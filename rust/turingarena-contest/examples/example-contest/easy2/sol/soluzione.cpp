#include <cstdio>
int main() {
#ifdef EVAL
    freopen("input.txt", "r", stdin);
    freopen("output.txt", "w", stdout);
#endif
    int N, max = -1;
    scanf("%d", &N);
    for (int i=0; i<N; i++) {
        int x, y;
        scanf("%d%d", &x, &y);
        x += y;
        if (x & 1 || max > x); else max = x;
    }
    printf("%d\n", max);
}
