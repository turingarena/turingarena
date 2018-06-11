from collections import namedtuple
from contextlib import contextmanager, ExitStack

from turingarena import *
from turingarena.driver.client import SandboxError, DriverClient, DriverProcessClient
from turingarena.driver.engine import DriverClientEngine
from turingarena.driver.proxy import MethodProxy
from turingarena.sandbox.client import SandboxClient, SandboxProcessClient

logger = logging.getLogger(__name__)


class Algorithm(namedtuple("Algorithm", [
    "source_name", "language_name", "interface_name",
])):
    @contextmanager
    def run(self, time_limit=None):
        with ExitStack() as stack:
            sandbox_dir = os.environ["TURINGARENA_SANDBOX_DIR"]

            sandbox_client = SandboxClient(sandbox_dir)
            sandbox_process_dir = stack.enter_context(sandbox_client.run(
                source_name=self.source_name,
                language_name=self.language_name,
                interface_name=self.interface_name,
            ))

            sandbox_process_client = SandboxProcessClient(sandbox_process_dir)

            driver_dir = os.environ["TURINGARENA_DRIVER_DIR"]

            driver_client = DriverClient(driver_dir)
            driver_process_dir = stack.enter_context(
                driver_client.run_driver(
                    interface_name=self.interface_name,
                    sandbox_process_dir=sandbox_process_dir,
                )
            )

            driver_process_client = DriverProcessClient(driver_process_dir)


            try:
                with driver_process_client.connect() as connection:
                    algorithm_process = AlgorithmProcess(connection)
                    with algorithm_process.run(time_limit):
                        try:
                            yield algorithm_process
                        except InterfaceExit:
                            pass
                        algorithm_process.exit()
            except SandboxError:
                info = sandbox_process_client.get_info(wait=True)
                if info.error:
                    raise AlgorithmRuntimeError(info.error) from None
                raise
            sandbox_process_client.get_info(wait=True)


class AlgorithmSection:
    def __init__(self):
        self.info_before = None
        self.info_after = None

    def finished(self, info_before, info_after):
        self.info_before = info_before
        self.info_after = info_after

    @contextmanager
    def run(self, time_limit):
        # FIXME: implement time limit
        yield self

    # FIXME: obsolete
    @contextmanager
    def _old_run(self, time_limit):
        info_before = sandbox.get_info()
        yield self
        info_after = sandbox.get_info()
        self.finished(info_before, info_after)
        if time_limit is not None and self.time_usage > time_limit:
            raise TimeLimitExceeded(self.time_usage, time_limit)

    @property
    def time_usage(self):
        return self.info_after.time_usage - self.info_before.time_usage


class AlgorithmProcess(AlgorithmSection):
    def __init__(self, connection):
        super().__init__()
        self._engine = DriverClientEngine(connection)

        self.procedures = MethodProxy(self._engine, has_return_value=False)
        self.functions = MethodProxy(self._engine, has_return_value=True)

        self.call = self.functions  # FIXME: for partial compatibility

    def section(self, *, time_limit=None):
        section_info = AlgorithmSection()
        return section_info.run(self.sandbox, time_limit=time_limit)

    def limit_memory(self, value):
        info = self.sandbox.get_info()
        if info.memory_usage > value:
            raise MemoryLimitExceeded(info.memory_usage, value)

    def exit(self):
        self._engine.send_exit()
