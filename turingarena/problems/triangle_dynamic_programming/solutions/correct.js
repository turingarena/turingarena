function max(a, b) {
    return a > b ? a : b;
}

function find_best_sum() {
    dyn = new Array(N+1);
    for (var i = 0; i <= N; i++)
        dyn[i] = new Array(N+1);
    for (var i = 0; i <= N; i++)
        dyn[N][i] = 0;
    for (var i = N-1; i >= 0; i--)
        for (var j = 0; j < i; j++)
            dyn[i][j] = V[i][j] + max(dyn[i+1][j], dyn[i+1][j+1]);
    return dyn[1][0];
}