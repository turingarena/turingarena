function max_index(n, a) {
    var j = 0;
    for (var i = 0; i < n; i++)
        if(a[i] > a[j])
            j = i;
    return j;
}
