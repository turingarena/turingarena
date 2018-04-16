import random

from turingarena.evaluation import *
from turingarena.sandbox.exceptions import AlgorithmRuntimeError

algorithm = submitted_algorithm()

correct = False

for _ in range(10):
    a = random.randrange(0, 1000)
    b = random.randrange(0, 1000)

    try:
        print(f"{a:3d} + {b:3d} --->", end=" ")
        with algorithm.run() as process:
            c = process.call.sum(a, b)
        print(f"{c:4d}", end=" ")
    except AlgorithmRuntimeError as e:
        print(e)
        break
    if c != a + b:
        print("WRONG!")
        break
    print("correct")
else:  # no break occurred
    correct = True

evaluation_result(goals=dict(correct=correct))
