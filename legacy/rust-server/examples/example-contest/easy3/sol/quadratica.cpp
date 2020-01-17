#include <cstdio>
inline int max(int a, int b) {
    return a > b ? a : b;
}
int s[100000];
int main() {
#ifdef EVAL
    freopen("input.txt", "r", stdin);
    freopen("output.txt", "w", stdout);
#endif
    int N, ans = -1;
    scanf("%d", &N);
    for (int i=0; i<N; i++) {
        scanf("%d", s+i);
    }
    for (int i=0; i<N-1; i++)
        for (int j=i+1; j<N; j++)
            if ((s[i] + s[j]) % 2 == 0)
                ans = max(ans, s[i] + s[j]);
    printf("%d\n", ans);
}

