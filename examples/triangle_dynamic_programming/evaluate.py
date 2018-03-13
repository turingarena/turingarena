import random


def evaluate(algorithm):
    N = 10
    V = [
        [
            random.randrange(0, 100)
            for j in range(i)
        ]
        for i in range(N)
    ]

    right = solve(V)
    S = compute(algorithm, V)
    if right == S:
        print("correct!")
    else:
        print(S, "!=", right)
        print("WRONG!")


def solve(V):
    S = V[-1]
    for i in reversed(range(1, len(V) - 1)):
        S = [
            V[i][j] + max(S[j], S[j + 1])
            for j in range(i)
        ]

    [S] = S
    return S


def compute(algorithm, V):
    with algorithm.run(global_variables=dict(N=len(V), V=V)) as process:
        return process.call.find_best_sum()
