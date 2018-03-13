from skeleton import N, V

def find_best_sum():
    dyn = [[0 for j in range(N+1)] for i in range(N+1)]
    for i in range(N-1, -1, -1):
        for j in range(i):
            dyn[i][j] = V[i][j] + max(dyn[i+1][j], dyn[i+1][j+1])
    return dyn[1][0]
