import sys

from interfaces.exampleinterface import exampleinterface
from turingarena.runtime.sandbox import SandboxClient


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

client = SandboxClient()

solution = client.algorithm_create_process("solution")
solution.start()

iface = exampleinterface(
    downward_pipe=solution.downward_pipe,
    upward_pipe=solution.upward_pipe,
    main=main,
    callback_test=test
)

iface.main()
