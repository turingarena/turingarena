// evaluation_assert data["goals"]["quadratic"]
// evaluation_assert not data["goals"]["n_log_n"]
#include <vector>
#include <algorithm>

int n;
int* a;

std::vector<int> s;

void compute() {
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

    while(best_len) {
        s.push_back(best);
        best = prev[best];
        best_len--;
    }
}

int length() {
    return s.size();
}

int element(int i) {
    return s[s.size()-i-1];
}
