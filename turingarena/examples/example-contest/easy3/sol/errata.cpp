#include <cstdio>
inline int max(int a, int b) {
    return a > b ? a : b;
}
int main() {
#ifdef EVAL
    freopen("input.txt", "r", stdin);
    freopen("output.txt", "w", stdout);
#endif
    int N, ans = -1;
    int maxx = -1, maxx2 = -1;
    scanf("%d", &N);
    while (N--) {
        int x;
        scanf("%d", &x);
        if (x >= maxx) {
            maxx2 = maxx;
            maxx = x;
        } else if (x >= maxx2) {
            maxx2 = x;
        }
    }
    if (maxx >= 0 && maxx2 >= 0)
        ans = max(ans, maxx + maxx2);
    printf("%d\n", ans);
}

