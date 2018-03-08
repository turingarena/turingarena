def max_index(n, a):
    j = 0
    for i, e in enumerate(a):
        if e > a[j]:
            j = i
    return j