import threading
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena.protocol.driver.client import DriverClient, DriverProcessClient
from turingarena.protocol.driver.server import DriverServer
from turingarena.sandbox.client import SandboxClient
from turingarena.sandbox.server import SandboxServer


class ProxiedAlgorithm:
    def __init__(self, *, algorithm_dir, interface):
        self.algorithm_dir = algorithm_dir
        self.interface = interface

    @contextmanager
    def run(self, **global_variables):
        with TemporaryDirectory(prefix="sandbox_server_") as sandbox_dir:
            sandbox_server = SandboxServer(sandbox_dir)
            sandbox_client = SandboxClient(sandbox_dir)

            sandbox_server_thread = threading.Thread(target=sandbox_server.run)
            sandbox_server_thread.start()

            with sandbox_client.run(self.algorithm_dir) as sandbox_process_dir:
                with TemporaryDirectory(prefix="driver_server_") as driver_dir:
                    driver_server = DriverServer(driver_dir)
                    driver_client = DriverClient(driver_dir)

                    driver_server_thread = threading.Thread(target=driver_server.run)
                    driver_server_thread.start()

                    with driver_client.run(
                            interface=self.interface,
                            sandbox_process_dir=sandbox_process_dir,
                    ) as driver_process_dir:
                        with DriverProcessClient(
                                interface=self.interface,
                                driver_process_dir=driver_process_dir,
                        ).run() as engine:
                            engine.begin_main(**global_variables)
                            proxy = Proxy(engine=engine)
                            yield engine, proxy
                            engine.end_main()

                    driver_server.stop()
                    driver_server_thread.join()

            sandbox_server.stop()
            sandbox_server_thread.join()


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
