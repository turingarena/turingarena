import random

from turingarena import *


def solve(V):
    S = V[-1]
    for i in reversed(range(1, len(V) - 1)):
        S = [
            V[i][j] + max(S[j], S[j + 1])
            for j in range(i)
        ]

    [S] = S
    return S


N = 10
V = [
    [
        random.randrange(0, 100)
        for j in range(i)
    ]
    for i in range(N)
]

right = solve(V)

with run_algorithm(submission.source) as process:
    S = process.functions.find_best_sum(len(V), V)

if right == S:
    print("correct!")
else:
    print(S, "!=", right)
    print("WRONG!")
