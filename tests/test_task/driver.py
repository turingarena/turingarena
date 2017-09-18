import sys

from interfaces.exampleinterface import exampleinterface

from turingarena.runtime.sandbox import sandbox
from turingarena.runtime.data import rebased
from turingarena.runtime.sandbox import SandboxClient

solution = sandbox.create_process("solution")
solution.start()


with exampleinterface(solution) as driver:
    driver.test = lambda a, b: a + b

    driver.N = 10
    driver.M = 100
    driver.A = rebased(1, [None] * driver.N)

    driver.A[1:] = [i*i for i in range(1,1+driver.N)]

    S = driver.solve(3)

print("Answer:", S, file=sys.stderr)
