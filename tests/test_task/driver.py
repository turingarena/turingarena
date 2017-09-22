import sys

from interfaces.exampleinterface import exampleinterface

from turingarena.runtime.sandbox import sandbox
from turingarena.runtime.data import rebased


with sandbox.create_process("solution") as s, exampleinterface(s) as driver:
    driver.test = lambda a, b: a + b

    driver.N = 10
    driver.M = 100
    driver.A = rebased(1, [None] * driver.N)

    driver.A[1:] = [i*i for i in range(1,1+driver.N)]

    S = driver.solve(3)

print("Answer:", S, file=sys.stderr)
