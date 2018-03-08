import random

import pkg_resources
import pytest

from turingarena.problem import AlgorithmicProblem

interface_text = pkg_resources.resource_string(__name__, "interface.txt").decode()


def evaluate(algorithm):
    cases = [
        (random.randrange(0, 1000), random.randrange(0, 1000))
        for _ in range(20)
    ]
    for a, b in cases:
        c = compute(algorithm, a, b)
        print(f"{a:3d} + {b:3d} == {c:4d}", end=" ")
        if c == a + b:
            print("correct!")
        else:
            print("WRONG!")


def compute(algorithm, a, b):
    with algorithm.run() as process:
        return process.call.sum(a, b)


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
        ("wrong.cpp", "c++"),
        ("correct.js", "javascript"),
    ]
)
def test_solution(solution, language):
    problem.evaluate(
        pkg_resources.resource_string(__name__, f"solutions/{solution}").decode(),
        language=language,
    )
