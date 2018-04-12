import logging
import os
import threading
from contextlib import contextmanager, ExitStack
from tempfile import TemporaryDirectory

from turingarena.interface.driver.client import DriverClient, DriverProcessClient
from turingarena.interface.driver.server import DriverServer
from turingarena.interface.interface import InterfaceDefinition
from turingarena.problem.problem import load_interface_text
from turingarena.sandbox.client import SandboxClient, SandboxProcessClient
from turingarena.sandbox.exceptions import AlgorithmRuntimeError, TimeLimitExceeded, MemoryLimitExceeded
from turingarena.sandbox.server import SandboxServer
from turingarena.sandbox.source import AlgorithmSource

logger = logging.getLogger(__name__)


class Algorithm:
    def __init__(self, algorithm_dir, *, interface_name):
        self.algorithm_dir = algorithm_dir
        self.interface_name = interface_name

    @staticmethod
    @contextmanager
    def load(*, source_text, interface_name, language):
        interface_text = load_interface_text(interface_name)
        # FIXME: we should not compile the source here
        interface = InterfaceDefinition.compile(interface_text)
        algorithm_source = AlgorithmSource.load(
            source_text,
            interface=interface,
            language=language,
        )

        with TemporaryDirectory(dir="/tmp") as temp_dir:
            algorithm_dir = os.path.join(temp_dir, "algorithm")
            algorithm_source.compile(algorithm_dir)

            yield Algorithm(algorithm_dir, interface_name=interface_name)

    @contextmanager
    def run(self, global_variables=None, time_limit=None):
        if global_variables is None:
            global_variables = {}

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
                driver_client.run_driver(
                    interface_name=self.interface_name,
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
                with algorithm_process.section(time_limit=time_limit):
                    yield algorithm_process
                    driver_process_client.send_end_main()
            finally:
                info = sandbox_process_client.wait()
                if info.error:
                    raise AlgorithmRuntimeError(info.error)


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
    def section(self, *, time_limit=None):
        section_info = AlgorithmSection()
        info_before = self.sandbox.get_info()
        yield section_info
        info_after = self.sandbox.get_info()
        section_info.finished(info_before, info_after)
        if time_limit is not None and section_info.time_usage > time_limit:
            raise TimeLimitExceeded(section_info.time_usage, time_limit)

    def limit_memory(self, value):
        info = self.sandbox.get_info()
        if info.memory_usage > value:
            raise MemoryLimitExceeded(info.memory_usage, value)
