import threading
from contextlib import contextmanager, ExitStack
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
        with ExitStack() as stack:
            sandbox_dir = stack.enter_context(
                TemporaryDirectory(dir="/dev/shm", prefix="sandbox_server_")
            )

            sandbox_server = SandboxServer(sandbox_dir)
            sandbox_client = SandboxClient(sandbox_dir)

            sandbox_server_thread = threading.Thread(target=sandbox_server.run)
            sandbox_server_thread.start()
            stack.callback(sandbox_server_thread.join)
            stack.callback(sandbox_server.stop)

            sandbox_process_dir = stack.enter_context(sandbox_client.run(self.algorithm_dir))
            driver_dir = stack.enter_context(
                TemporaryDirectory(dir="/dev/shm", prefix="driver_server_")
            )

            driver_server = DriverServer(driver_dir)
            driver_client = DriverClient(driver_dir)

            driver_server_thread = threading.Thread(target=driver_server.run)
            driver_server_thread.start()
            stack.callback(driver_server_thread.join)
            stack.callback(driver_server.stop)

            driver_process_dir = stack.enter_context(
                driver_client.run(
                    interface=self.interface,
                    sandbox_process_dir=sandbox_process_dir,
                )
            )

            engine = stack.enter_context(
                DriverProcessClient(
                    interface=self.interface,
                    driver_process_dir=driver_process_dir,
                ).run()
            )

            engine.begin_main(**global_variables)
            proxy = Proxy(engine=engine)
            yield engine, proxy
            engine.end_main()


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
