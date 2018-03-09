import random

import pkg_resources
import pytest

from turingarena.problem import AlgorithmicProblem

interface_text = pkg_resources.resource_string(__name__, "interface.txt").decode()


def evaluate(algorithm):
    for _ in range(10):
        a = [
            random.randrange(0, 100)
            for _ in range(10)
        ]

        index = compute(algorithm, a)

        if a[index] == max(a):
            print("correct!")
        else:
            print("WRONG!")


def compute(algorithm, a):
    with algorithm.run() as process:
        return process.call.max_index(len(a), a)


problem = AlgorithmicProblem(
    interface_text=interface_text,
    evaluator=evaluate,
)


@pytest.mark.parametrize(
    "solution,language",
    [
        ("correct.cpp", "c++"),
        ("correct.py", "python"),
        ("Correct.java", "java"),
        ("correct.js", "javascript"),
        ("wrong.cpp", "c++"),
    ]
)
def test_solution(solution, language):
    problem.evaluate(
        pkg_resources.resource_string(__name__, f"solutions/{solution}").decode(),
        language=language,
    )
