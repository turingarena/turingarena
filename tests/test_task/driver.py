import sys

from interfaces.exampleinterface import exampleinterface

from turingarena.runtime.data import rebased
from turingarena.runtime.sandbox import SandboxClient


class Driver(exampleinterface):
    def main(self):
        self.N = 10
        self.M = 100
        self.A = rebased(1, [i*i for i in range(1, 1 + self.N)])

        S = self.solve(3)

        print("Answer:", S, file=sys.stderr)

        return 0

    def test(self, a, b):
        return a + b

client = SandboxClient()

solution = client.algorithm_create_process("solution")
solution.start()

Driver(solution)
