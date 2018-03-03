import random

from turingarena.problem import AlgorithmicProblem

interface_text = """
    function sum(int a, int b) -> int;
    main {
        var int a, b, c;
        input a, b;
        call sum(a, b) -> c;
        output c;
    }
"""


def compute(algorithm, a, b):
    with algorithm.run() as process:
        return process.call.sum(a, b)


def evaluate(algorithm):
    cases = [
        (random.randrange(0, 1000), random.randrange(0, 1000))
        for _ in range(20)
    ]
    for a, b in cases:
        c = compute(algorithm, a, b)
        print(f"{a:3d} + {b:3d} == {c:4d}", end=" ")
        if c == a + b:
            print("correct!")
        else:
            print("WRONG!")


problem = AlgorithmicProblem(
    interface_text=interface_text,
    evaluator=evaluate,
)


def test_correct():
    problem.evaluate(
        "int sum(int a, int b) { return a+b; }",
        language="c++",
    )
