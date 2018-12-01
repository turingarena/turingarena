import random

import turingarena as ta

for _ in range(10):
    a = random.choices(range(10 ** 4, 10 ** 5), k=20)

    try:
        with ta.run_algorithm(ta.submission.source) as process:
            index = process.functions.max_index(len(a), a)
        if a[index] == max(a):
            print("correct!")
        else:
            ta.goals["correct"] = False
            print("WRONG!")
    except ta.AlgorithmError as e:
        ta.goals["correct"] = False
        print(e)

ta.goals.setdefault("correct", True)
