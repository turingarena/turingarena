import random

import turingarena as ta
import turingarena.evallib.algorithm

for _ in range(10):
    value_range = range(10 ** 3, 5 * 10 ** 3)
    a, b = random.choices(value_range, k=2)

    try:
        print(f"{a} + {b} -->", end="")
        with turingarena.evallib.algorithm.run_algorithm(ta.submission.source) as process:
            c = process.functions.sum(a, b)
        print(f" {c}", end="")
        if c == a + b:
            print(" correct", end="")
        else:
            print("  WRONG!", end="")
            ta.goals["correct"] = False
        print(
            f" ("
            f"time: {int(process.time_usage * 1000000)} us, "
            f"memory: {process.current_memory_usage}, "
            f"peak: {process.peak_memory_usage})"
            f")"
        )
    except ta.AlgorithmError as e:
        print(f" {e}")
        ta.goals["correct"] = False

ta.goals.setdefault("correct", True)
