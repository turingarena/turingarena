import random

from turingarena import *

algorithm = submitted_algorithm()

all_passed = True
for _ in range(10):
    a = random.choices(range(10 ** 4, 10 ** 5), k=20)

    try:
        with algorithm.run() as process:
            process.call.sort(len(a), a)
            index = process.call.max_index(len(a), a)
    except AlgorithmError as e:
        print(e)
        all_passed = False
    if a[index] == max_value:
        print("correct!")
    else:
        print("WRONG!")
        all_passed = False

evaluation_result(goals=dict(correct=all_passed))
