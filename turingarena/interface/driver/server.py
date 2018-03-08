import logging
from contextlib import ExitStack

from turingarena.interface.driver.commands import ProxyRequest
from turingarena.interface.driver.connection import DRIVER_QUEUE, DRIVER_PROCESS_QUEUE
from turingarena.interface.engine import drive_interface
from turingarena.interface.exceptions import CommunicationBroken
from turingarena.interface.interface import InterfaceDefinition
from turingarena.metaserver import MetaServer
from turingarena.pipeboundary import PipeBoundary
from turingarena.sandbox.client import SandboxProcessClient

logger = logging.getLogger(__name__)


class DriverServer(MetaServer):
    def get_queue_descriptor(self):
        return DRIVER_QUEUE

    def create_child_server(self, child_server_dir, *, sandbox_process_dir, interface_text):
        return DriverProcessServer(
            sandbox_process_dir=sandbox_process_dir,
            interface_text=interface_text,
            driver_process_dir=child_server_dir,
        )

    def run_child_server(self, child_server):
        child_server.run()

    def create_response(self, child_server_dir):
        return dict(driver_process_dir=child_server_dir)


class DriverProcessServer:
    def __init__(self, *, interface_text, sandbox_process_dir, driver_process_dir):
        self.sandbox_dir = sandbox_process_dir
        self.boundary = PipeBoundary(driver_process_dir)
        self.interface = InterfaceDefinition.compile(interface_text)
        self.main = self.interface.body.scope.main["main"]

        self.boundary.create_queue(DRIVER_PROCESS_QUEUE)
        self.run_driver_iterator = None

    def run(self):
        with ExitStack() as stack:
            logger.debug("connecting to process...")
            sandbox_connection = stack.enter_context(
                SandboxProcessClient(self.sandbox_dir).connect()
            )
            logger.debug("connected")

            self.run_driver_iterator = drive_interface(
                sandbox_connection=sandbox_connection,
                driver_boundary=self.boundary,
                interface=self.interface
            )
            self.process_requests()

    def handle_request(self, request):
        logger.debug(f"handling driver request {request!s:.50}")
        current_request = ProxyRequest.deserialize(
            iter(request.splitlines()),
            interface_signature=self.interface.signature,
        )

        try:
            response = self.run_driver_iterator.send(current_request)
        except CommunicationBroken as e:
            logger.warning(f"communication with process broken")
            return {
                "sandbox_error": "communication broken",
            }

        assert all(isinstance(x, int) for x in response)
        logger.debug(f"handling driver request {request!s:.10} with response {response!s:.50}")

        return {
            "response": "\n".join(str(x) for x in response)
        }

    def process_requests(self):
        assert next(self.run_driver_iterator) is None
        while True:
            logger.debug(f"waiting for driver request...")
            self.boundary.handle_request(DRIVER_PROCESS_QUEUE, self.handle_request)
            try:
                assert next(self.run_driver_iterator) is None
            except StopIteration:
                break
