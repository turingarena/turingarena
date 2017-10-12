import sys

from interfaces.exampleinterface import exampleinterface

from turingarena.runtime.sandbox import sandbox

with sandbox.create_process("solution") as s, exampleinterface(s) as driver:
    driver.N = 10
    driver.M = 100
    driver.A = [i * i for i in range(driver.N)]

    S = driver.solve(3, callback_test=lambda a, b: a + b)

print("Answer:", S, file=sys.stderr)
