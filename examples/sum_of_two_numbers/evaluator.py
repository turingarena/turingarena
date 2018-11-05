import random

import turingarena as ta
import turingarena.driver.exceptions

all_passed = True
for _ in range(10):
    value_range = range(10 ** 3, 5 * 10 ** 3)
    a, b = random.choices(value_range, k=2)

    try:
        print(f"{a} + {b} -->", end="")
        with ta.run_algorithm(ta.submission.source) as process:
            c = process.functions.sum(a, b)
        print(f" {c}", end="")
        if c == a + b:
            print(" correct", end="")
        else:
            print("  WRONG!", end="")
            all_passed = False
        print(f" ({int(process.time_usage * 1000000)} us)")
    except turingarena.driver.exceptions.AlgorithmError as e:
        print(f" {e}")
        all_passed = False

ta.evaluation.data(dict(goals=dict(correct=all_passed)))
