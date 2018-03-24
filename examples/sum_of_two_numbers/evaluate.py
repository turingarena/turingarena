import random
from functools import lru_cache


def evaluate(algorithm):
    cases = [
        (random.randrange(0, 1000), random.randrange(0, 1000))
        for _ in range(20)
    ]
    return dict(goals=dict(
        correct=all(
            evaluate_test_case(algorithm, a, b)
            for a, b in cases
        ),
        correct_fraction=sum(
            evaluate_test_case(algorithm, a, b)
            for a, b in cases
        ) / len(cases),
    ))


def evaluate_test_case(algorithm, a, b):
    c = compute(algorithm, a, b)
    print(f"{a:3d} + {b:3d} == {c:4d}", end=" ")
    if c == a + b:
        print("correct!")
        return True
    else:
        print("WRONG!")
        return False


@lru_cache(maxsize=None)
def compute(algorithm, a, b):
    with algorithm.run() as process:
        return process.call.sum(a, b)
