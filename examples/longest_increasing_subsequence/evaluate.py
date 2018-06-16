import random
import sys

from turingarena import *


def run(algorithm, a, time_limit=None):
    with algorithm.run(time_limit=time_limit) as process:
        process.procedures.compute(len(a) ,a)
        subsequence = [x for i, x in enumerate(a) if process.functions.takes(i)]
    print(f"Time usage: {process.time_usage}", file=sys.stderr)
    return subsequence


def get_optimal_subsequence(a):
    correct_algorithm = algorithm("longest_increasing_subsequence:solutions/correct.cpp")
    return run(correct_algorithm, a)


def create_random_instance(n, digits=6):
    value_range = range(10 ** (digits - 1), 10 ** digits)
    return random.sample(value_range, k=n)


def main():
    algorithm = submitted_algorithm()
    goals = {
        "exponential": True,
        "quadratic": True,
        "n_log_n": True,
    }

    for gs, ns in [
        (["exponential", "quadratic", "n_log_n"], [10] * 3),
        (["quadratic", "n_log_n"], [100]),
        (["n_log_n"], [1000]),
    ]:
        for n in ns:
            if not any(goals[g] for g in gs):
                break

            print(f"Testing n={n}", file=sys.stderr)

            a = create_random_instance(n)
            optimal_subsequence = get_optimal_subsequence(a)
            try:
                subsequence = run(algorithm, a, time_limit=0.001)
            except AlgorithmError as e:
                print("Error:", e)
                correct = False
            else:
                print("Subsequence:", subsequence)
                print("Optimal subsequence:", optimal_subsequence)
                correct = (
                    is_subsequence(subsequence, a) and
                    is_increasing(subsequence) and
                    len(subsequence) == len(optimal_subsequence)
                )
                print("Correct:", correct)
            if not correct:
                for g in gs:
                    goals[g] = False
    evaluation_data(dict(goals=goals))


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
