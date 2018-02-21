def goal(entry):
    N = 10
    M = 100
    A = [i * i for i in range(N)]
    with entry.run(N=N, M=M, A=A) as (process, p):
        S = p.solve(3, test=lambda a, b: a + b)

    return S == 9
