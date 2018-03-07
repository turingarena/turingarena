import random

from turingarena.problem import AlgorithmicProblem

interface_text = """
    var int N;
    var int[][] V;

    function find_best_sum() -> int;

    main {
        input N;
        alloc V : N;
        for(i : N) {
            alloc V[i] : i;
            for(j : i) {
                input V[i][j];
            }
        }

        var int S;
        call find_best_sum() -> S;
        output S;
    }
"""


def evaluate(algorithm):
    N = 10
    V = [
        [
            random.randrange(0, 100)
            for j in range(i)
        ]
        for i in range(N)
    ]

    right = solve(V)
    S = compute(algorithm, V)
    if right == S:
        print("correct!")
    else:
        print(S, "!=", right)
        print("WRONG!")


def solve(V):
    S = V[-1]
    for i in reversed(range(1, len(V) - 1)):
        S = [
            V[i][j] + max(S[j], S[j + 1])
            for j in range(i)
        ]

    [S] = S
    return S


def compute(algorithm, V):
    with algorithm.run(global_variables=dict(N=len(V), V=V)) as process:
        return process.call.find_best_sum()


problem = AlgorithmicProblem(
    interface_text=interface_text,
    evaluator=evaluate,
)


def test_correct():
    problem.evaluate(
        """
            #include <algorithm>
            
            int N;
            int** V;
            int find_best_sum() {
                int dyn[N+1][N+1];
                for(int i = 0; i < N+1; i++)
                    dyn[N][i] = 0;                
                for(int i = N-1; i >= 0; i--)
                    for(int j = 0; j < i; j++)
                        dyn[i][j] = V[i][j] + std::max(dyn[i+1][j], dyn[i+1][j+1]);            
                return dyn[1][0];
            }
        """,
        language="c++",
    )
