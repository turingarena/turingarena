import io
from abc import abstractmethod
from collections.__init__ import namedtuple

from turingarena.driver.client.processinfo import SandboxProcessInfo

SandboxProcessConnection = namedtuple("SandboxProcessConnection", [
    "downward",
    "upward",
    "manager",
])


class ProcessManager:
    def get_status(self, kill_reason=None) -> SandboxProcessInfo:
        return self._do_get_status(kill_reason)

    @abstractmethod
    def _do_get_status(self, kill_reason):
        pass


class FailedProcessManager(ProcessManager):
    def __init__(self, reason):
        self.reason = reason

    def _do_get_status(self, kill_reason):
        return SandboxProcessInfo(
            time_usage=0.0,
            current_memory_usage=0,
            peak_memory_usage=0,
            error=self.reason,
        )


def create_failed_connection(reason):
    return SandboxProcessConnection(
        upward=io.StringIO(),
        downward=io.StringIO(),
        manager=FailedProcessManager(reason),
    )
