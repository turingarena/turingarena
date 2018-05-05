import random

from turingarena import *

algorithm = submitted_algorithm()

all_passed = True
for _ in range(10):
    n = 20
    a = random.choices(range(10 ** 4, 10 ** 5), k=n)

    try:
        with algorithm.run() as process:
            process.call.sort(n, a)
            b = [process.call.get_element(i) for i in range(n)]
    except AlgorithmError as e:
        print(e)
        all_passed = False
    if b == sorted(a):
        print("correct!")
    else:
        print("WRONG!")
        all_passed = False

evaluation_result(goals=dict(correct=all_passed))
