import logging
import subprocess
from collections import namedtuple
from contextlib import contextmanager

from turingarena import InterfaceExit, TimeLimitExceeded, AlgorithmError
from turingarena.driver.connection import DriverProcessConnection
from turingarena.driver.engine import DriverClientEngine
from turingarena.driver.proxy import MethodProxy

logger = logging.getLogger(__name__)


class Program(namedtuple("Program", [
    "source_path", "interface_path",
])):
    @contextmanager
    def run(self, time_limit=None):
        with subprocess.Popen(
                [
                    "python3",
                    "-m",
                    "turingarena_impl.driver.server",
                    self.source_path,
                    self.interface_path,
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True,
        ) as p:
            connection = DriverProcessConnection(
                downward=p.stdin,
                upward=p.stdout,
            )

            process = Process(connection)
            with process.run(time_limit=time_limit):
                try:
                    yield process
                except InterfaceExit:
                    pass
            process.exit()


class ProcessSection:
    def __init__(self, engine):
        self.info_before = None
        self.info_after = None
        self._engine = engine

    @contextmanager
    def _run(self, *, time_limit):
        self.info_before = self._engine.get_info()
        yield self
        self.info_after = self._engine.get_info()

        if time_limit is not None and self.time_usage > time_limit:
            raise TimeLimitExceeded(
                self,
                f"Time limit exceeded: {self.time_usage} {time_limit}",
                self.info_after,
            )

    @property
    def time_usage(self):
        return self.info_after.time_usage - self.info_before.time_usage


class Process(ProcessSection):
    def __init__(self, connection):
        super().__init__(engine=DriverClientEngine(self, connection))

        self.procedures = MethodProxy(self._engine, has_return_value=False)
        self.functions = MethodProxy(self._engine, has_return_value=True)
        self.terminated = False

    def section(self, *, time_limit=None):
        section_info = ProcessSection(self._engine)
        return section_info._run(time_limit=time_limit)

    def checkpoint(self):
        self._engine.send_checkpoint()

    def exit(self):
        self._engine.send_exit()

    def fail(self, message, exc_type=AlgorithmError):
        if self.terminated:
            info = None
        else:
            info = self._engine.get_info(kill=True)

        raise exc_type(self, message, info)

    @contextmanager
    def run(self, **kwargs):
        assert not self.terminated
        self._engine.get_response_ok()  # ready
        with self._run(**kwargs) as section:
            yield section
        self.terminated = True

    def check(self, condition, message, exc_type=AlgorithmError):
        if not condition:
            self.fail(message, exc_type)
