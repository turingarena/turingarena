// evaluation_assert not data["goals"]["correct"]

#include <algorithm>

int *b;

void sort(int n, int* a) {
    b = new int[n];
    for(int i = 0; i < n; i++)
        b[i] = a[i];
    // std::sort(b, b+n);
}

int get_element(int i) {
    return b[i];
}
