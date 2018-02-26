import logging
import threading
from contextlib import contextmanager, ExitStack
from tempfile import TemporaryDirectory

from turingarena.protocol.driver.client import DriverClient, DriverProcessClient, DriverRunningProcess
from turingarena.protocol.driver.server import DriverServer
from turingarena.protocol.module import load_interface_signature
from turingarena.sandbox.client import SandboxClient, SandboxProcessClient
from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.sandbox.server import SandboxServer

logger = logging.getLogger(__name__)


class Algorithm:
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
            sandbox_process_client = SandboxProcessClient(sandbox_process_dir)

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

            driver_connection = stack.enter_context(
                DriverProcessClient(driver_process_dir).connect()
            )

            interface_signature = load_interface_signature(self.interface)
            running_process = DriverRunningProcess(
                interface_signature=interface_signature,
                connection=driver_connection,
            )

            try:
                running_process.begin_main(global_variables)
                algorithm_process = AlgorithmProcess(
                    sandbox=sandbox_process_client,
                    driver=running_process,
                )
                yield algorithm_process, running_process.proxy
                running_process.end_main()
            finally:
                info = sandbox_process_client.wait()
                if info.error:
                    raise AlgorithmRuntimeError(
                        info.error,
                        info.stacktrace,
                    )


class AlgorithmSectionInfo:
    def __init__(self):
        self.info_before = None
        self.info_after = None

    def finished(self, info_before, info_after):
        self.info_before = info_before
        self.info_after = info_after

    @property
    def time_usage(self):
        return self.info_after.time_usage - self.info_before.time_usage


class AlgorithmProcess:
    def __init__(self, *, sandbox, driver):
        self.sandbox = sandbox
        self.driver = driver

    @contextmanager
    def section(self):
        section_info = AlgorithmSectionInfo()
        info_before = self.sandbox.get_info()
        try:
            yield section_info
        finally:
            info_after = self.sandbox.get_info()
            section_info.finished(info_before, info_after)
