int **b;
int **c;
int *seq;

void build_sequence(int x, int i, int j) {
    if (i == 0 || j == 0) {
        return;
    }

    if (b[i][j] == 1) {
        seq[x] = X[i - 1];
        build_sequence(x - 1, i - 1, j - 1);
    } else if (b[i][j] == 2) {
        build_sequence(x, i - 1, j);
    } else {
        build_sequence(x, i, j - 1);
    }
}

int compute(int M, int X, int N, int Y) {
    b = new int*[M+1];
    c = new int*[M+1];

    for (int i = 0; i <= M; i++) {
        b[i] = new int[N+1];
        c[i] = new int[N+1];
    }

    for (int i = 0; i <= M; i++) {
        c[i][0] = 0;
    }

    for (int j = 0; j <= N; j++) {
        c[0][j] = 0;
    }

    for (int i = 1; i <= M; i++) {
        for (int j = 1; j <= N; j++) {
            if (X[i-1] == Y[j-1]) {
                c[i][j] = c[i-1][j-1] + 1;
                b[i][j] = 1;
            } else if (c[i-1][j] >= c[i][j-1]) {
                c[i][j] = c[i-1][j];
                b[i][j] = 2;
            } else {
                c[i][j] = c[i][j-1];
                b[i][j] = 3;
            }
        }
    }

    seq = new int[c[M][N]];
    build_sequence(c[M][N] - 1, M, N);

    return c[M][N]
}

int element(int i) {
    return seq[i];
}


