import logging
import os
import threading
from contextlib import contextmanager, ExitStack
from tempfile import TemporaryDirectory

from turingarena.interface.driver.client import DriverClient, DriverProcessClient
from turingarena.interface.driver.server import DriverServer
from turingarena.interface.interface import InterfaceDefinition
from turingarena.sandbox.client import SandboxClient, SandboxProcessClient
from turingarena.sandbox.exceptions import AlgorithmRuntimeError, TimeLimitExceeded, MemoryLimitExceeded
from turingarena.sandbox.server import SandboxServer
from turingarena.sandbox.source import AlgorithmSource

logger = logging.getLogger(__name__)


class Algorithm:
    def __init__(self, algorithm_dir):
        self.algorithm_dir = algorithm_dir

    @staticmethod
    @contextmanager
    def load(*, source_text, interface_text, language):
        interface = InterfaceDefinition.compile(interface_text)
        algorithm_source = AlgorithmSource.load(
            source_text,
            interface=interface,
            language=language,
        )

        with TemporaryDirectory(dir="/tmp") as temp_dir:
            algorithm_dir = os.path.join(temp_dir, "algorithm")
            algorithm_source.compile(algorithm_dir)

            yield Algorithm(algorithm_dir)

    @contextmanager
    def run(self, global_variables=None, time_limit=None):
        if global_variables is None:
            global_variables = {}

        with open(os.path.join(self.algorithm_dir, "interface.txt")) as f:
            interface_text = f.read()

        with ExitStack() as stack:
            sandbox_dir = stack.enter_context(
                TemporaryDirectory(dir="/tmp", prefix="sandbox_server_")
            )

            sandbox_server = SandboxServer(sandbox_dir)
            sandbox_client = SandboxClient(sandbox_dir)

            sandbox_server_thread = threading.Thread(target=sandbox_server.run)
            sandbox_server_thread.start()
            stack.callback(sandbox_server_thread.join)
            stack.callback(sandbox_server.stop)

            sandbox_process_dir = stack.enter_context(sandbox_client.run(self.algorithm_dir))
            driver_dir = stack.enter_context(
                TemporaryDirectory(dir="/tmp", prefix="driver_server_")
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
                    interface_text=interface_text,
                    sandbox_process_dir=sandbox_process_dir,
                )
            )

            driver_process_client = DriverProcessClient(driver_process_dir)

            try:
                driver_process_client.send_begin_main(global_variables)
                algorithm_process = AlgorithmProcess(
                    sandbox=sandbox_process_client,
                    driver=driver_process_client,
                )
                yield algorithm_process
                driver_process_client.send_end_main()

                if time_limit is not None:
                    algorithm_process.time_limit(time_limit)
            finally:
                info = sandbox_process_client.wait()
                if info.error:
                    raise AlgorithmRuntimeError(
                        info.error,
                        info.stacktrace,
                    )


class AlgorithmSection:
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
        self.call = driver.proxy

    @contextmanager
    def section(self):
        section_info = AlgorithmSection()
        info_before = self.sandbox.get_info()
        try:
            yield section_info
        finally:
            info_after = self.sandbox.get_info()
            section_info.finished(info_before, info_after)

    def time_limit(self, value):
        info = self.sandbox.get_info()
        if info.time_usage > value:
            raise TimeLimitExceeded(info.time_usage, value)

    def memory_limit(self, value):
        info = self.sandbox.get_info()
        if info.memory_usage > value:
            raise MemoryLimitExceeded(info.memory_usage, value)
