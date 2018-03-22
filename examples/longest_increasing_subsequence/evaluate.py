import random


def evaluate(submission):
    exponential = all(
        evaluate_test_case(submission, n)
        for n in [5] * 10 + [10] * 10
    )
    quadratic = exponential and all(
        evaluate_test_case(submission, n)
        for n in [100] * 10 + [1000] * 10
    )
    n_log_n = quadratic and all(
        evaluate_test_case(submission, n)
        for n in [10000] * 5
    )

    return dict(
        goals=dict(
            exponential=exponential,
            quadratic=quadratic,
            n_log_n=n_log_n,
        ),
    )


def evaluate_test_case(submission, n):
    digits = 6
    value_range = range(10 ** digits, 10 ** (digits + 1))
    a = random.sample(value_range, n)

    with submission.run(global_variables=dict(n=len(a), a=a)) as process:
        process.call.compute()
        l = process.call.length()
        s = [process.call.element(i) for i in range(l)]

    with context.algorithms["correct.cpp"].run(
            global_variables=dict(n=len(a), a=a)
    ) as process:
        process.call.compute()
        opt_l = process.call.length()
        opt_s = [process.call.element(i) for i in range(l)]

    print(s)
    print(opt_s)
    if n <= 10:
        exponential_s = compute_subsequence_exponential(a)
        print(exponential_s)

    return True


def compute_subsequence_exponential(seq):
    assert len(seq) <= 10
    return max(
        (s for s in subsequences(seq) if increasing(s)),
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
    if not a:
        return True
    if not b:
        return False
    try:
        start = b.index(a[0])
    except ValueError:
        return False
    return is_subsequence(a[1:], b[start + 1:])


def increasing(s):
    return all(x < y for x, y in zip(s, s[1:]))
