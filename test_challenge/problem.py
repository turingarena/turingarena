def checker(algorithm):
    N = 10
    M = 100
    A = [i * i for i in range(N)]
    with algorithm.run(global_variables=locals()) as (process, p):
        S = p.solve(3, test=lambda a, b: a + b)

    if S == 9:
        print("correct!")
    else:
        print("wrong!")
