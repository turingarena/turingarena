import sys

from interfaces.exampleinterface import exampleinterface

from turingarena.sandbox.client import sandbox

with sandbox.create_process("solution") as s, exampleinterface(s) as proxy:
    proxy.N = 10
    proxy.M = 100
    proxy.A = [i * i for i in range(proxy.N)]

    S = proxy.solve(3, callback_test=lambda a, b: a + b)

print("Answer:", S, file=sys.stderr)
