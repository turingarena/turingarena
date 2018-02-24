import logging
import sys
from contextlib import ExitStack
from tempfile import TemporaryDirectory

from turingarena.pipeboundary import PipeBoundarySide, PipeBoundary
from turingarena.protocol.driver.connection import DriverProcessConnection, DRIVER_PROCESS_CHANNEL
from turingarena.protocol.driver.engine import InterfaceEngine
from turingarena.protocol.exceptions import CommunicationBroken
from turingarena.protocol.module import load_interface_definition
from turingarena.sandbox.client import SandboxProcessClient

logger = logging.getLogger(__name__)


class DriverProcessServer:
    def __init__(self, *, interface, sandbox_dir, process_dir):
        self.sandbox_dir = sandbox_dir
        self.boundary = PipeBoundary(process_dir)
        self.interface_definition = load_interface_definition(interface)
        self.main = self.interface_definition.body.scope.main["main"]

        self.boundary.create_channel(DRIVER_PROCESS_CHANNEL)

    def run(self):
        with ExitStack() as stack:
            sys.stdout.close()

            driver_connection = DriverProcessConnection(
                **stack.enter_context(
                    self.boundary.open_channel(DRIVER_PROCESS_CHANNEL, PipeBoundarySide.SERVER)
                )
            )

            logger.debug("connecting to process...")
            sandbox_connection = stack.enter_context(
                SandboxProcessClient(self.sandbox_dir).connect()
            )
            logger.debug("connected")

            engine = InterfaceEngine(
                sandbox_connection=sandbox_connection,
                driver_connection=driver_connection,
                interface=self.interface_definition
            )

            try:
                engine.run()
            except CommunicationBroken as e:
                logger.warning(f"communication with process broken")
                logger.exception(e)


def driver_server(*, interface, sandbox_dir):
    prefix = "turingarena_driver_"
    with TemporaryDirectory(prefix=prefix) as process_dir:
        server = DriverProcessServer(
            interface=interface,
            sandbox_dir=sandbox_dir,
            process_dir=process_dir
        )
        print(process_dir)
        server.run()
