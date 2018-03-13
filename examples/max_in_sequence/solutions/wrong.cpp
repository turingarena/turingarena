int max_index(int n, int* a) {
    int j = 0;
    for(int i = 0; i < n; i++)
        if(a[i] > a[j])
            j = i;
    return j - j%2;
}
