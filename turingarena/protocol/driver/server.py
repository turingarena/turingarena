import logging
from contextlib import ExitStack

from turingarena.metaserver import MetaServer
from turingarena.pipeboundary import PipeBoundarySide, PipeBoundary
from turingarena.protocol.driver.connection import DriverProcessConnection, DRIVER_PROCESS_CHANNEL, DRIVER_QUEUE
from turingarena.protocol.driver.engine import InterfaceEngine
from turingarena.protocol.exceptions import CommunicationBroken
from turingarena.protocol.module import load_interface_definition
from turingarena.sandbox.client import SandboxProcessClient

logger = logging.getLogger(__name__)


class DriverServer(MetaServer):
    def get_queue_descriptor(self):
        return DRIVER_QUEUE

    def create_child_server(self, child_server_dir, *, sandbox_process_dir, interface):
        return DriverProcessServer(
            sandbox_process_dir=sandbox_process_dir,
            interface=interface,
            driver_process_dir=child_server_dir,
        )

    def run_child_server(self, child_server):
        child_server.run()

    def create_response(self, child_server_dir):
        return dict(driver_process_dir=child_server_dir)


class DriverProcessServer:
    def __init__(self, *, interface, sandbox_process_dir, driver_process_dir):
        self.sandbox_dir = sandbox_process_dir
        self.boundary = PipeBoundary(driver_process_dir)
        self.interface_definition = load_interface_definition(interface)
        self.main = self.interface_definition.body.scope.main["main"]

        self.boundary.create_channel(DRIVER_PROCESS_CHANNEL)

    def run(self):
        with ExitStack() as stack:
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
