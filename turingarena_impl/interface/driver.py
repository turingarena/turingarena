import logging
from contextlib import contextmanager, ExitStack

from turingarena.driver.connection import DRIVER_QUEUE, DRIVER_PROCESS_CHANNEL, DriverProcessConnection
from turingarena.pipeboundary import PipeBoundary, PipeBoundarySide
from turingarena.sandbox.client import SandboxProcessClient
from turingarena_impl.interface.engine import NodeExecutionContext, DriverRequestStream, DriverResponseStream
from turingarena_impl.interface.exceptions import CommunicationBroken
from turingarena_impl.interface.interface import InterfaceDefinition
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
                request_stream=DriverRequestStream(driver_connection),
                response_stream=DriverResponseStream(driver_connection),  # TODO
                sandbox_connection=sandbox_connection,
                sandbox_process_client=sandbox_process_client,
            )
            self.interface.run_driver(context)

    # FIXME: everything below is obsolete

    def handle_request(self, request):
        current_request = self.deserialize(request)
        logger.debug(f"received request {type(current_request)}")
        try:
            response = self.run_driver_iterator.send(current_request)
        except CommunicationBroken:
            logger.warning(f"communication with process broken")
            return {
                "sandbox_error": "communication broken",
            }

        assert all(isinstance(x, int) for x in response)
        return {
            "response": "\n".join(str(x) for x in response)
        }

    def process_requests(self):
        assert next(self.run_driver_iterator) is None
        while True:
            self.boundary.handle_request(DRIVER_PROCESS_QUEUE, self.handle_request)
            try:
                assert next(self.run_driver_iterator) is None
            except StopIteration:
                break
