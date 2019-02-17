#include <vector>
#include <algorithm>

int max_len;

std::vector<bool> taken;

void compute(int n, int *s) {
    int prev[n], len[n];
    int best = -1;

    max_len = 0;
    for(int i = 0; i < n; i++) {
        prev[i] = -1;
        len[i] = 1;
        for(int j = 0; j < i; j++) {
            if(s[i] > s[j] && len[j]+1 > len[i]) {
                len[i] = len[j]+1;
                prev[i] = j;
            }
        }
        if(len[i] > max_len) {
            max_len = len[i];
            best = i;
        }
    }

    taken.resize(n);
    while(best >= 0) {
        taken[best] = true;
        best = prev[best];
    }
}


int max_length() {
    return max_len;
}

int takes(int i) {
    return taken[i];
}

int color_of(int i) {
    return 32;
}

