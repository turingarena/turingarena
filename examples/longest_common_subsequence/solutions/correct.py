s = []

def compute(M, X, N, Y):
    global s
    b = [[0 for _ in range(M + 1)] for _ in range(N + 1)]
    c = [[0 for _ in range(M + 1)] for _ in range(N + 1)]
    for i in range(1, M + 1):
        for j in range(1, M + 1):
            if X[i - 1] == Y[j - 1]:
                c[i][j] = c[i-1][j-1] + 1
                b[i][j] = 1
            elif c[i-1][j] >= c[i][j-1]:
                c[i][j] = c[i-1][j]
                b[i][j] = 2
            else:
                c[i][j] = c[i][j-1]
                b[i][j] = 3
    l = c[M][N]
    i = M
    j = N
    while i > 0 and j > 0:
        if b[i][j] == 1:
            s.insert(0, X[i - 1])
            i -= 1
            j -= 1
        elif b[i][j] == 2:
            i -= 1
        else:
            j -= 1

    return l


def element(i):
    return s[i]


