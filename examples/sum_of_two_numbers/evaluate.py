import random

from turingarena.evaluation import *
from turingarena.sandbox.exceptions import AlgorithmRuntimeError

algorithm = submitted_algorithm(interface_name="sum_of_two_numbers")

correct = True

for _ in range(10):
    a, b = random.randrange(0, 1000), random.randrange(0, 1000)

    try:
        print(f"{a:3d} + {b:3d} ==", end=" ")
        with algorithm.run() as process:
            c = process.call.sum(a, b)
        print(f"{c:4d}", end=" ")
    except AlgorithmRuntimeError as e:
        print("error!")
        correct = False
        break

    if c == a + b:
        print("correct!")
    else:
        print("WRONG!")
        correct = False
        break

evaluation_result(goals=dict(correct=correct))
