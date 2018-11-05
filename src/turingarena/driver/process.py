from contextlib import contextmanager

from turingarena.driver.engine import DriverClientEngine, CallRequest
from turingarena.driver.exceptions import AlgorithmError, TimeLimitExceeded
from turingarena.driver.proxy import MethodProxy


class ProcessSection:
    def __init__(self, engine):
        self.info_before = None
        self.info_after = None
        self._engine = engine

    @contextmanager
    def _run(self, *, time_limit):
        # self.info_before = self._engine.get_info()
        yield self
        # self.info_after = self._engine.get_info()

        if time_limit is not None and self.time_usage > time_limit:
            raise TimeLimitExceeded(
                self,
                f"Time limit exceeded: {self.time_usage} {time_limit}",
            )

    @property
    def time_usage(self):
        # return self.info_after.time_usage - self.info_before.time_usage
        return 0


class Process(ProcessSection):
    def __init__(self, connection):
        super().__init__(engine=DriverClientEngine(self, connection))

        self.procedures = MethodProxy(self, has_return_value=False)
        self.functions = MethodProxy(self, has_return_value=True)

    def section(self, *, time_limit=None):
        section_info = ProcessSection(self._engine)
        return section_info._run(time_limit=time_limit)

    def call(self, method_name, *args, has_return_value, callbacks=None):
        if callbacks is None:
            callbacks = {}

        request = CallRequest(
            method_name=method_name,
            arguments=args,
            has_return_value=has_return_value,
            callbacks=callbacks,
        )
        return self._engine.call(request)

    def check(self, condition, message, exc_type=AlgorithmError):
        if not condition:
            self.fail(message, exc_type)

    def checkpoint(self):
        self._engine.checkpoint()

    def exit(self):
        self._engine.exit()

    def stop(self):
        self._engine.stop()

    def fail(self, message, exc_type=AlgorithmError):
        raise exc_type(self, message)

    @contextmanager
    def run(self, **kwargs):
        with self._run(**kwargs) as section:
            yield section
