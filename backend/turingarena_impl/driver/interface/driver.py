import logging
from contextlib import contextmanager, ExitStack

from turingarena.driver.connection import DRIVER_QUEUE, DRIVER_PROCESS_CHANNEL, DriverProcessConnection
from turingarena.pipeboundary import PipeBoundary, PipeBoundarySide
from turingarena.sandbox.client import SandboxProcessClient
from turingarena_impl.driver.interface.execution import NodeExecutionContext
from turingarena_impl.driver.interface.interface import InterfaceDefinition
from turingarena_impl.driver.interface.variables import ReferenceDirection
from turingarena_impl.metaserver import MetaServer

logger = logging.getLogger(__name__)


class DriverServer(MetaServer):
    def get_queue_descriptor(self):
        return DRIVER_QUEUE

    @contextmanager
    def run_child_server(self, child_server_dir, *, sandbox_process_dir, interface_name):
        server = DriverProcessServer(
            sandbox_process_dir=sandbox_process_dir,
            interface_name=interface_name,
            driver_process_dir=child_server_dir,
        )
        yield
        server.run()

    def create_response(self, child_server_dir):
        return dict(driver_process_dir=child_server_dir)


class DriverProcessServer:
    def __init__(self, *, interface_name, sandbox_process_dir, driver_process_dir):
        self.sandbox_dir = sandbox_process_dir
        self.boundary = PipeBoundary(driver_process_dir)
        self.interface = InterfaceDefinition.load(interface_name)

        self.boundary.create_channel(DRIVER_PROCESS_CHANNEL)

    def run(self):
        with ExitStack() as stack:
            logger.debug("connecting to process...")

            sandbox_process_client = SandboxProcessClient(self.sandbox_dir)
            sandbox_connection = stack.enter_context(
                sandbox_process_client.connect()
            )

            pipes = stack.enter_context(self.boundary.open_channel(DRIVER_PROCESS_CHANNEL, PipeBoundarySide.SERVER))
            driver_connection = DriverProcessConnection(**pipes)

            context = NodeExecutionContext(
                bindings={},
                phase=None,
                direction=None,
                driver_connection=driver_connection,
                sandbox_connection=sandbox_connection,
                sandbox_process_client=sandbox_process_client,
            )
            self.interface.run_driver(context)
