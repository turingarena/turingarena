// evaluation_assert data["goals"]["n_log_n"]
#include <vector>
#include <algorithm>
#include <cassert>
#include <limits>

using std::vector;

vector<bool> taken;

void compute(int n, int *a) {
    int values[n+1];
    vector<int> antichains[n+1];
    int prev[n+1], len[n+1];
    int best = 0;

    taken.resize(n);

    values[0] = std::numeric_limits<int>::min();
    for(int i = 0; i < n; i++) values[i+1] = a[i];

    antichains[0].push_back(0);

    for(int i = 1; i <= n; i++) {
        auto p = std::upper_bound(antichains, antichains+n+1, i, [&](int i, vector<int>& ac) -> bool {
            return ac.empty() || values[i] < values[ac.back()];
        });
        assert(p > antichains);
        assert(p <= antichains+n);

        prev[i] = p[-1].back();
        assert(prev[i] >= 0);
        assert(prev[i] <= n);

        len[i] = len[prev[i]] + 1;
        if(len[i] > len[best]) best = i;
        p[0].push_back(i);
    }

    while(best) {
        assert(best >= 0);
        assert(best <= n);
        taken[best] = true;
        best = prev[best];
    }
}


int takes(int i) {
    return taken[i+1];
}
