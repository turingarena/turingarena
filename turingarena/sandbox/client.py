import logging
from contextlib import contextmanager

from turingarena.common import ImmutableObject
from turingarena.pipeboundary import PipeBoundarySide, PipeBoundary
from turingarena.sandbox.connection import SandboxProcessConnection, \
    SANDBOX_PROCESS_CHANNEL, SANDBOX_QUEUE, SANDBOX_REQUEST_QUEUE

logger = logging.getLogger(__name__)


class SandboxException(Exception):
    pass


class SandboxClient:
    def __init__(self, sandbox_dir):
        self.boundary = PipeBoundary(sandbox_dir)

    @contextmanager
    def run(self, algorithm_dir):
        response = self.boundary.send_request(
            SANDBOX_QUEUE,
            algorithm_dir=algorithm_dir,
        )
        yield response["sandbox_process_dir"]


class SandboxProcessInfo(ImmutableObject):
    __slots__ = ["error", "stacktrace", "time_usage", "memory_usage"]

    def __init__(self, *, time_usage, memory_usage, **kwargs):
        super().__init__(
            time_usage=float(time_usage),
            memory_usage=int(memory_usage),
            **kwargs,
        )


class SandboxProcessClient:
    def __init__(self, directory):
        self.boundary = PipeBoundary(directory)

    def get_info(self, *, wait=False):
        response = self.boundary.send_request(
            SANDBOX_REQUEST_QUEUE,
            wait=str(int(bool(wait))),
        )
        return SandboxProcessInfo(**response)

    @contextmanager
    def connect(self):
        logger.debug("connecting to process...")
        with self.boundary.open_channel(SANDBOX_PROCESS_CHANNEL, PipeBoundarySide.CLIENT) as pipes:
            yield SandboxProcessConnection(**pipes)

    def wait(self):
        return self.get_info(wait=True)
