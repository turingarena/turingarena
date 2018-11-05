import random

import turingarena as ta

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
            ta.goals["correct"] = False
        print(f" ({int(process.time_usage * 1000000)} us)")
    except ta.AlgorithmError as e:
        print(f" {e}")
        ta.goals["correct"] = False

ta.goals.setdefault("correct", True)
