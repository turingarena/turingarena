import sys

from interfaces.exampleinterface import exampleinterface


def main():
    iface.N = 10
    iface.M = 100
    iface.A.alloc(1, iface.N)

    for i in range(1, 1 + iface.N):
        iface.A[i] = i * i

    S = iface.solve(3)

    print("Answer:", S, file=sys.stderr)

def test(a, b):
    return a + b

iface = exampleinterface(
    downward_pipe=sys.stdout,
    upward_pipe=sys.stdin,
    main=main,
    callback_test=test
)
iface.main()
