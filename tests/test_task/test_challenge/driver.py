import sys

from turingarena_protocols.test_challenge import exampleinterface

from turingarena.protocol.proxy.python.client import Implementation, Interface
from turingarena.protocol.proxy.python.engine import ProxyEngine
from turingarena.sandbox.client import Algorithm

solution = Implementation(
    interface=Interface("test_challenge", "exampleinterface"),
    algorithm=Algorithm("solution"),
)

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
