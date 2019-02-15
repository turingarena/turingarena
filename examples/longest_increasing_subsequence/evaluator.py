import random

import turingarena as ta

DEBUG = False

def run(algorithm, a):
    with ta.run_algorithm(algorithm, time_limit=0.05) as process:
        process.procedures.compute(len(a), a)
        subsequence = [x for i, x in enumerate(a) if process.functions.takes(i)]
    if DEBUG:
        print(f"Time usage: {process.time_usage}")
    return subsequence


def get_optimal_subsequence(a):
    correct_algorithm = "solutions/correct.cpp"
    return run(correct_algorithm, a)


def create_random_instance(n, digits=6):
    value_range = range(10 ** (digits - 1), 10 ** digits)
    return random.sample(value_range, k=n)


def main():
    algorithm = ta.submission.source

    for gs, ns in [
        (["exponential", "quadratic", "n_log_n"], [10, 50, 100]),
        (["quadratic", "n_log_n"], [500, 750, 1000]),
        (["n_log_n"], [3000, 6000, 10000]),
    ]:
        for n in ns:
            if not any(ta.goals.get(g, True) for g in gs):
                break

            print(f"Testing N = {n}...\t", end="")

            a = create_random_instance(n)
            optimal_subsequence = get_optimal_subsequence(a)
            try:
                subsequence = run(algorithm, a)
            except ta.AlgorithmError as e:
                print(f"[WRONG: {e}]")
                correct = False
            else:
                if DEBUG:
                    print("Subsequence:", subsequence)
                    print("Optimal subsequence:", optimal_subsequence)
                correct = (
                        is_subsequence(subsequence, a) and
                        is_increasing(subsequence) and
                        len(subsequence) == len(optimal_subsequence)
                )
            if correct:
                print("[CORRECT]")
            else:
                for g in gs:
                    ta.goals[g] = False
    for goal in (
        "exponential",
        "quadratic",
        "n_log_n",
    ):
        ta.goals.setdefault(goal, True)

    print(ta.goals)


def optimal_subsequence_exponential(a):
    assert len(a) <= 10
    return max(
        (s for s in subsequences(a) if is_increasing(s)),
        key=len,
    )


def subsequences(seq):
    if not seq:
        yield []
    else:
        [first, *rest] = seq
        for s in subsequences(rest):
            yield [first] + s
            yield s


def is_subsequence(a, b):
    j = 0
    for x in a:
        try:
            j += b[j:].index(x) + 1
        except ValueError:
            return False
    return True


def is_increasing(s):
    return all(x < y for x, y in zip(s, s[1:]))


def test_correct_algorithm():
    for _ in range(10):
        a = create_random_instance(10, digits=2)
        s = get_optimal_subsequence(a)
        print(s, a)
        assert is_subsequence(s, a)
        assert is_increasing(s)
        assert len(s) == len(optimal_subsequence_exponential(a))


if __name__ == "__main__":
    main()
