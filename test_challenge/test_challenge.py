from turingarena.problem import algorithmic_problem


@algorithmic_problem("test_challenge:test_interface")
def test_problem(context):
    N = 10
    M = 100
    A = [i * i for i in range(N)]
    with context.algorithm.run(N=N, M=M, A=A) as (process, p):
        S = p.solve(3, test=lambda a, b: a + b)

    if S == 9:
        context.feedback.success("correct!")
    else:
        context.feedback.info("wrong!")
