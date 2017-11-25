from turingarena.problem import Problem

problem = Problem()

problem.implementation_entry(
    "entry",
    protocol_name="test_challenge",
    interface_name="exampleinterface",
)


@problem.goal
def goal(entry):
    N = 10
    M = 100
    A = [i * i for i in range(N)]
    with entry.run(N=N, M=M, A=A) as p:
        S = p.solve(3, test=lambda a, b: a + b)

    return S == 9
