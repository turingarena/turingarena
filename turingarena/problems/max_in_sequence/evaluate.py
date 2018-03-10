import random


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
