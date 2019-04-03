import random

import turingarena as ta

for _ in range(20):
    value_range = range(10 ** ta.parameters.digits, 5 * 10 ** ta.parameters.digits)
    a, b = random.choices(value_range, k=2)

    print(f"Testing with a = {a} b = {b} ...", end="")
    try:
        def give_divisor(d):
            if a % d != 0 or b % d != 0:
                print(f"WRONG: Fornisci un divisore comune ({d}) che non è valido!")
                ta.goals["correct_NO_certificate"] = False
            else:
                print(f"Correct! Certificato verificato: come divisore comune hai fornito un numero valido ({d}).")

        def give_multipliers(x, y):
            if x*a + y*b != 1:
                print(f"WRONG: Fornisci due moltiplicatori x={x} ed y={y} per i quali non vale che x*a + y*b = 1.")
                ta.goals["correct_YES_certificate"] = False
            else:
                print(f"Correct! Certificato verificato: come moltiplicatori hai fornito x={x} e y={y} ed ho verificato che x*a + y*b = 1.")

        with ta.run_algorithm("solutions/correct.py") as p:
            expected_answer = p.functions.are_coprime(a, b, callbacks=[give_divisor, give_multipliers])

        with ta.run_algorithm(ta.submission.source) as p:
            obtained_answer = p.functions.are_coprime(a, b, callbacks=[give_divisor, give_multipliers])
    except ta.AlgorithmError as e:
        print(f" error: {e}")
        ta.goals.setdefault("correct_answer", True)
        ta.goals.setdefault("correct_NO_certificate", True)
        ta.goals.setdefault("correct_YES_certificate", True)
        
    if obtained_answer == 0:
        print(f" your answer: {a} and {b} are NOT coprime", end="")
    else:
        print(f" your answer: {a} and {b} are coprime", end="")
    if obtained_answer == expected_answer:
        print(" correct yes/no answer", end="")
    else:
        print("  (WRONG!)", end="")
        ta.goals["correct_answer"] = False
    print(f"(time: {int(p.time_usage * 1000000)} us)")



ta.goals.setdefault("correct_answer", True)
ta.goals.setdefault("correct_NO_certificate", True)
ta.goals.setdefault("correct_YES_certificate", True)
print(ta.goals)
