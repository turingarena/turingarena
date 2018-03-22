#include <vector>
#include <algorithm>

int n;
int* a;

std::vector<int> s;

void compute() {
    std::vector<std::vector<int>> antichains;

    std::vector<int> a {::a, ::a+n};
    for(int v : a) {
        auto p = std::upper_bound(antichains.begin(), antichains.end(), v, [&](int v, auto& antichain) -> bool {
            return antichain.back() > v;
        });
        if(p == antichains.end()) {
            antichains.push_back({ v });
        } else {
            p->push_back(v);
        }
    }

    for(auto antichain : antichains) {
        s.push_back(antichain.back());
    }
}

int length() {
    return s.size();
}

int element(int i) {
    return s[i];
}
