import sys

from interfaces.exampleinterface import exampleinterface
from turingarena.runtime.sandbox import SandboxClient

class Driver(exampleinterface):
    def main(self):
        self.N = 10
        self.M = 100
        self.A.alloc(1, self.N)

        for i in range(1, 1 + self.N):
            self.A[i] = i * i

        S = self.solve(3)

        print("Answer:", S, file=sys.stderr)

        return 0

    def test(self, a, b):
        return a + b

client = SandboxClient()

solution = client.algorithm_create_process("solution")
solution.start()

driver = Driver(
    downward_pipe=solution.downward_pipe,
    upward_pipe=solution.upward_pipe,
)

driver.start()
