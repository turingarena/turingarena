import threading
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena.pipeboundary import PipeBoundarySide
from turingarena.protocol.driver.client import DriverClient
from turingarena.sandbox.client import SandboxClient
from turingarena.sandbox.connection import SandboxBoundary
from turingarena.sandbox.server import SandboxServer


class ProxiedAlgorithm:
    def __init__(self, *, algorithm_dir, interface):
        self.algorithm_dir = algorithm_dir
        self.interface = interface

    @contextmanager
    def run(self, **global_variables):
        with TemporaryDirectory("sandbox_server_") as server_dir:
            boundary = SandboxBoundary(server_dir)
            boundary.init()

            def server_target():
                with boundary.connect(PipeBoundarySide.SERVER) as server_connection:
                    server = SandboxServer(server_connection)
                    server.run()

            server_thread = threading.Thread(target=server_target)
            server_thread.start()

            with boundary.connect(PipeBoundarySide.CLIENT) as client_connection:
                client = SandboxClient(client_connection)

                with client.run(self.algorithm_dir) as process:
                    with DriverClient().run(interface=self.interface, process=process) as engine:
                        engine.begin_main(**global_variables)
                        proxy = Proxy(engine=engine)
                        yield process, proxy
                        engine.end_main()
            server_thread.join()


class Proxy:
    def __init__(self, engine):
        self._engine = engine

    def __getattr__(self, item):
        try:
            self._engine.interface_signature.functions[item]
        except KeyError:
            raise AttributeError

        def method(*args, **kwargs):
            return self._engine.call(item, args=args, callbacks_impl=kwargs)

        return method
