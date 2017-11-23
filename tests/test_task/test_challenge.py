import sys

from turingarena_proxies.test_challenge import exampleinterface

from turingarena.problem import Problem
from turingarena.protocol import ProtocolIdentifier

problem = Problem()

problem.implementation_entry(
    "entry",
    protocol_id=ProtocolIdentifier("test_challenge"),
    interface_name="exampleinterface",
)


@problem.goal
def goal(entry):
    with entry.run() as connection:
        p = exampleinterface(connection)

        p.N = 10
        p.M = 100
        p.A = [i * i for i in range(p.N)]

        S = p.solve(3, callback_test=lambda a, b: a + b)

    print("Answer:", S, file=sys.stderr)
