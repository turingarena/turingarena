import logging
from contextlib import ExitStack, contextmanager

from turingarena.interface.driver.commands import deserialize_request
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

        self.boundary.create_queue(DRIVER_PROCESS_QUEUE)
        self.run_driver_iterator = None

    def run(self):
        with ExitStack() as stack:
            logger.debug("connecting to process...")
            sandbox_connection = stack.enter_context(
                SandboxProcessClient(self.sandbox_dir).connect()
            )

            self.run_driver_iterator = drive_interface(
                sandbox_connection=sandbox_connection,
                interface=self.interface
            )
            self.process_requests()

    def handle_request(self, request):
        current_request = self.deserialize(request)
        logger.debug(f"recieved request {current_request}")
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

    def deserialize(self, request):
        deserializer = deserialize_request()

        assert next(deserializer) is None

        lines = request.splitlines()
        lines_it = iter(lines)
        try:
            for line in lines_it:
                deserializer.send(line)
        except StopIteration as e:
            extra_lines = list(lines_it)
            if extra_lines:
                raise ValueError(f"extra lines '{extra_lines!s:.50}'") from None
            result = e.value
        else:
            raise ValueError(f"too few lines")

        return result

    def process_requests(self):
        assert next(self.run_driver_iterator) is None
        while True:
            self.boundary.handle_request(DRIVER_PROCESS_QUEUE, self.handle_request)
            try:
                assert next(self.run_driver_iterator) is None
            except StopIteration:
                break
