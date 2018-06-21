import logging
from contextlib import contextmanager

from turingarena.processinfo import SandboxProcessInfo
from turingarena.driver.connection import DriverProcessConnection, \
    DRIVER_PROCESS_CHANNEL, SANDBOX_PROCESS_CHANNEL, SANDBOX_QUEUE, SANDBOX_REQUEST_QUEUE, SandboxProcessConnection
from turingarena.pipeboundary import PipeBoundary, PipeBoundarySide

logger = logging.getLogger(__name__)


class SandboxError(Exception):
    pass


class DriverProcessClient:
    def __init__(self, driver_process_dir):
        self.boundary = PipeBoundary(driver_process_dir)

    @contextmanager
    def connect(self):
        logger.debug("connecting to driver...")
        with self.boundary.open_channel(DRIVER_PROCESS_CHANNEL, PipeBoundarySide.CLIENT) as pipes:
            yield DriverProcessConnection(**pipes)


class SandboxException(Exception):
    pass


class SandboxClient:
    def __init__(self, sandbox_dir):
        self.boundary = PipeBoundary(sandbox_dir)

    @contextmanager
    def run(self, *, language_name, source_name, interface_name):
        response = self.boundary.send_request(
            SANDBOX_QUEUE,
            language_name=language_name,
            source_name=source_name,
            interface_name=interface_name,
        )
        yield response["sandbox_process_dir"]


class SandboxProcessClient:
    def __init__(self, directory):
        self.boundary = PipeBoundary(directory)

    def get_info(self, *, wait=False):
        response = self.boundary.send_request(
            SANDBOX_REQUEST_QUEUE,
            wait=str(int(bool(wait))),
        )
        info = SandboxProcessInfo.from_payloads(response)
        logger.info(f"Process info: {info}")
        return info

    @contextmanager
    def connect(self):
        logger.debug("connecting to process...")
        with self.boundary.open_channel(SANDBOX_PROCESS_CHANNEL, PipeBoundarySide.CLIENT) as pipes:
            yield SandboxProcessConnection(**pipes)
