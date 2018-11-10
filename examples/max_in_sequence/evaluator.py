import random

from turingarena import *
from turingarena.evallib.algorithm import run_algorithm

all_passed = True
for _ in range(10):
    a = random.choices(range(10 ** 4, 10 ** 5), k=20)

    try:
        with run_algorithm(submission.source) as process:
            index = process.functions.max_index(len(a), a)
        if a[index] == max(a):
            print("correct!")
        else:
            print("WRONG!")
            all_passed = False
    except AlgorithmError as e:
        print(e)
        all_passed = False
