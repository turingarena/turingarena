import random


def evaluate(algorithm):
    return dict(goals={
        "correct": all(
            evaluate_test_case(algorithm, (random.randrange(0, 1000), random.randrange(0, 1000)))
            for _ in range(20)
        ),
    })


def evaluate_test_case(algorithm, case):
    a, b = case
    c = compute(algorithm, a, b)
    print(f"{a:3d} + {b:3d} == {c:4d}", end=" ")
    if c == a + b:
        print("correct!")
        return True
    else:
        print("WRONG!")
        return False


def compute(algorithm, a, b):
    with algorithm.run() as process:
        return process.call.sum(a, b)
