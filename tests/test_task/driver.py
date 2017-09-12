import sys

import subprocess
from interfaces.exampleinterface import exampleinterface


def main():
    iface.N = 10
    iface.M = 100
    iface.A.alloc(1, iface.N)

    for i in range(1, 1 + iface.N):
        iface.A[i] = i * i

    S = iface.solve(3)

    print("Answer:", S, file=sys.stderr)

    return 0

def test(a, b):
    return a + b

solution = subprocess.Popen(
    "./solution",
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    universal_newlines=True,
)

iface = exampleinterface(
    downward_pipe=solution.stdin,
    upward_pipe=solution.stdout,
    main=main,
    callback_test=test
)

iface.main()
