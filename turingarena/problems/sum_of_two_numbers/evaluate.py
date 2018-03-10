import random


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
