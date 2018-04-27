import random

from turingarena import *

algorithm = submitted_algorithm()

for _ in range(10):
    a = random.choices(range(10 ** 4, 10 ** 5), k=20)
    max_value = max(a)

    try:
        with algorithm.run() as process:
            index = process.call.max_index(len(a), a)
    except AlgorithmError as e:
        print(e)
        correct = False
        break

    if a[index] != max_value:
        print("WRONG!")
        correct = False
        break
    print("correct!")
else:
    correct = True

evaluation_result(goals=dict(correct=correct))
