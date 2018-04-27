import random

from turingarena import *

algorithm = submitted_algorithm()

for _ in range(10):
    value_range = range(10 ** 3, 5 * 10 ** 3)
    a, b = random.choices(value_range, k=2)

    try:
        with algorithm.run() as process:
            c = process.call.sum(a, b)
    except AlgorithmError as e:
        print(f"{a} + {b} --> {e}")
        correct = False
        break
    if c != a + b:
        print(f"{a} + {b} --> {c} (wrong!)")
        correct = False
        break
    print(f"{a} + {b} --> {c} (correct)")
else:  # no break occurred
    correct = True

evaluation_result(goals=dict(correct=correct))
