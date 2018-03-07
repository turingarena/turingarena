int max_index(int n, int* a) {
    for(int j = 0, i = 0; i < n; i++)
        if(a[i] > a[j])
            j = i;
    return j;
}
