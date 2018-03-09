import random

import pkg_resources
import pytest

from turingarena.problem import AlgorithmicProblem

interface_text = pkg_resources.resource_string(__name__, "interface.txt").decode()


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


problem = AlgorithmicProblem(
    interface_text=interface_text,
    evaluator=evaluate,
)


@pytest.mark.parametrize(
    "solution,language",
    [
        ("correct.cpp", "c++"),
        ("Correct.java", "java"),
        ("correct.py", "python"),
        ("correct.js", "javascript"),
    ]
)
def test_solution(solution, language):
    problem.evaluate(
        pkg_resources.resource_string(__name__, f"solutions/{solution}").decode(),
        language=language,
    )
