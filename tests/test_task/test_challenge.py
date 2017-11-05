from turingarena_protocols.test_challenge import exampleinterface

from turingarena.problem import Problem
from turingarena.protocol.proxy.python.engine import ProxyEngine

problem = Problem()

problem.implementation_submission_item(
    "solution",
    protocol_name="test_challenge",
    interface_name="exampleinterface",
)

@problem.goal
def goal(solution):
    with solution.run() as connection:
        class Data:
            pass

        data = Data()
        data.N = 10
        data.M = 100
        data.A = [i * i for i in range(data.N)]

        proxy = ProxyEngine(
            interface_signature=exampleinterface,
            instance=data,
            connection=connection,
        )
        S = proxy.call("solve", [3], {"test": lambda a, b: a + b})

        proxy.end_main()

    print("Answer:", S, file=sys.stderr)
