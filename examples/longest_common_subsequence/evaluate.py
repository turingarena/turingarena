import random

from turingarena.evaluation import *
from turingarena.sandbox.exceptions import AlgorithmRuntimeError


def LCS_length(x, y):
    m = len(x)
    n = len(y)
    c = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if x[i - 1] == y[j - 1]:
                c[i][j] = c[i - 1][j - 1] + 1
            elif c[i - 1][j] >= c[i][j - 1]:
                c[i][j] = c[i - 1][j]
            else:
                c[i][j] = c[i][j - 1]

    return c[m][n]


def is_valid_solution(x, y, sol):
    if len(sol) != LCS_length(x, y):
        return False
    for c in sol:
        try:
            i = x.index(c)
            j = y.index(c)
        except ValueError:
            return False
        x = x[i + 1:]
        y = y[j + 1:]
    return True


def evaluate_test_case(submission, N):
    x = [
        random.randint(0, 10)
        for _ in range(N)
    ]
    y = [
        random.randint(0, 10)
        for _ in range(N)
    ]
    m = len(x)
    n = len(y)
    with submission.run(global_variables=dict(X=x, Y=y, M=m, N=n)) as process:
        process.call.compute()
        sol = [
            process.call.element(i)
            for i in range(process.call.length())
        ]
        return is_valid_solution(x, y, sol)


cases = []
algorithm = submitted_algorithm()

try:
    i = 0
    for n in [10] * 5 + [100, 1000]:
        i += 1
        if evaluate_test_case(algorithm, n):
            print(f'test case N = {n} correct')
            cases.append((i, n, True))
        else:
            print(f'test case N = {n} wrong')
            cases.append((i, n, False))
except AlgorithmRuntimeError:
    correct = False

evaluation_result(goals={
    f"case {i} (N={n})": "ok" if ok else "no"
    for i, n, ok in cases
})
