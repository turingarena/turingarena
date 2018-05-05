// evaluation_assert data["goals"]["correct"]

#include <vector>
#include <algorithm>

std::vector<int> b;

void sort(int n, int* a) {
    b = {a, a+n};
    std::sort(b.begin(), b.end());
}

int get_element(int i) {
    return b[i];
}
