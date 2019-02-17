import random, sys
import turingarena as ta

DEBUG = False

def run(algorithm, s):
    with ta.run_algorithm(algorithm, time_limit=0.05) as process:
        process.procedures.compute(len(s), s)
        subsequence_length = process.functions.max_length()
        subsequence = [x for i, x in enumerate(s) if process.functions.takes(i)]
        color = []
        for i in range(len(s)):
            color.append(process.functions.color_of(i))
    if DEBUG:
        print(f"Time usage: {process.time_usage}", file=sys.stderr)
    return (subsequence_length, subsequence, color)


def get_an_optimal_subsequence_of(s):
    correct_algorithm = "solutions/correct.cpp"
    return run(correct_algorithm, s)[1]


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

            s = create_random_instance(n)
            optimal_subsequence = get_an_optimal_subsequence_of(s)
            try:
                subsequence_length, subsequence, color = run(algorithm, s)
            except ta.AlgorithmError as e:
                print(f"[WRONG: {e}]")
                correct = False
            else:
                if DEBUG:
                    print("Declared maximum subsequence length:", subsequence_length)
                    print("Subsequence:", subsequence)
                    print("Optimal subsequence:", optimal_subsequence)
                    print("Coloring:", color)
                correct = (
                        is_subsequence(subsequence, s) and
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


def optimal_subsequence_exponential(s):
    assert len(s) <= 10
    return max(
        (ss for ss in subsequences_of(s) if is_increasing(ss)),
        key=len,
    )


def subsequences_of(s):
    if not s:
        yield []
    else:
        [first, *rest] = s
        for ss in subsequences_of(rest):
            yield [first] + ss
            yield ss


def is_subsequence(ss, s):
    j = 0
    for x in ss:
        try:
            j += s[j:].index(x) + 1
        except ValueError:
            return False
    return True


def is_increasing(s):
    return all(x < y for x, y in zip(s, s[1:]))


def test_correct_algorithm():
    for _ in range(10):
        s = create_random_instance(10, digits=2)
        ss = get_an_optimal_subsequence_of(s)
        print(ss, s)
        assert is_subsequence(ss, s)
        assert is_increasing(ss)
        assert len(ss) == len(optimal_subsequence_exponential(s))


if __name__ == "__main__":
    main()
