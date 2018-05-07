// evaluation_assert data["goals"]["quadratic"]
// evaluation_assert not data["goals"]["n_log_n"]
#include <vector>
#include <algorithm>

std::vector<bool> taken;

void compute(int n, int *a) {
    int prev[n], len[n];
    int best, best_len;

    best_len = 0;
    for(int i = 0; i < n; i++) {
        prev[i] = -1;
        len[i] = 1;
        for(int j = 0; j < i; j++) {
            if(a[i] > a[j] && len[j]+1 > len[i]) {
                len[i] = len[j]+1;
                prev[i] = j;
            }
        }
        if(len[i] > best_len) {
            best = i;
            best_len = len[i];
        }
    }

    taken.resize(n);
    while(best_len) {
        taken[best] = true;
        best = prev[best];
        best_len--;
    }
}

int takes(int i) {
    return taken[i];
}
