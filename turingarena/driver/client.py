import logging
from contextlib import contextmanager

from turingarena.driver.connection import DRIVER_QUEUE, DriverProcessConnection, \
    DRIVER_PROCESS_CHANNEL
from turingarena.driver.proxy import InterfaceProxy
from turingarena.pipeboundary import PipeBoundary, PipeBoundarySide

logger = logging.getLogger(__name__)


class SandboxError(Exception):
    pass


class DriverClient:
    def __init__(self, driver_dir):
        self.boundary = PipeBoundary(driver_dir)

    @contextmanager
    def run_driver(self, *, interface_name, sandbox_process_dir):
        response = self.boundary.send_request(
            DRIVER_QUEUE,
            interface_name=interface_name,
            sandbox_process_dir=sandbox_process_dir,
        )
        yield response["driver_process_dir"]


class DriverProcessClient:
    def __init__(self, driver_process_dir):
        self.boundary = PipeBoundary(driver_process_dir)
        self.proxy = InterfaceProxy(self)

    @contextmanager
    def connect(self):
        logger.debug("connecting to driver...")
        with self.boundary.open_channel(DRIVER_PROCESS_CHANNEL, PipeBoundarySide.CLIENT) as pipes:
            yield DriverProcessConnection(**pipes)
