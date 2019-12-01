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
    int maxpari = -1, maxpari2 = -1, maxdisp = -1, maxdisp2 = -1;
    scanf("%d", &N);
    while (N--) {
        int x;
        scanf("%d", &x);
        if (x & 1) {
            if (x >= maxdisp) {
                maxdisp2 = maxdisp;
                maxdisp = x;
            } else if (x >= maxdisp2) {
                maxdisp2 = x;
            }
        } else {
            if (x >= maxpari) {
                maxpari2 = maxpari;
                maxpari = x;
            } else if (x >= maxpari2) {
                maxpari2 = x;
            }
        }
    }
    if (maxpari >= 0 && maxpari2 >= 0)
        ans = max(ans, maxpari + maxpari2);
    if (maxdisp >= 0 && maxdisp2 >= 0)
        ans = max(ans, maxdisp + maxdisp2);
    printf("%d\n", ans);
}

