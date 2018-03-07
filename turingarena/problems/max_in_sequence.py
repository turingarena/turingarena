import random

from turingarena.problem import AlgorithmicProblem

interface_text = """
    function max_index(int n, int[] a) -> int;
    main {
        var int n;
        var int[] a;
        
        input n;
        alloc a : n;
        for(i : n) {
            input a[i];
        }
        
        var int index;
        call max_index(n, a) -> index;
        output index;
    }
"""


def evaluate(algorithm):
    for _ in range(10):
        a = [
            random.randrange(0, 100)
            for _ in range(10)
        ]

        index = compute(algorithm, a)

        if a[index] == max(a):
            print("correct!")
        else:
            print("WRONG!")


def compute(algorithm, a):
    with algorithm.run() as process:
        return process.call.max_index(len(a), a)


problem = AlgorithmicProblem(
    interface_text=interface_text,
    evaluator=evaluate,
)


def test_correct():
    problem.evaluate(
        """
            int max_index(int n, int* a) {
                int j = 0;
                for(int i = 0; i < n; i++) {
                    if(a[i] > a[j]) j = i;
                }
                return j;
            }
        """,
        language="c++",
    )


def test_wrong():
    problem.evaluate(
        """
            int max_index(int n, int* a) {
                int j = 0;
                for(int i = 0; i < n; i++) {
                    if(a[i] > a[j]) j = i;
                }
                return j-j%2;
            }
        """,
        language="c++",
    )
