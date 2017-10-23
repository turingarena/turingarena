import sys

from protocol import exampleinterface
from turingarena.sandbox.client import Algorithm

solution = Algorithm("solution")

with solution.create_process() as s, exampleinterface(s) as proxy:
    proxy.N = 10
    proxy.M = 100
    proxy.A = [i * i for i in range(proxy.N)]

    S = proxy.solve(3, callback_test=lambda a, b: a + b)

print("Answer:", S, file=sys.stderr)
