import logging
import tempfile
from contextlib import ExitStack
from threading import Thread

from turingarena.pipeboundary import PipeBoundarySide, PipeBoundary
from turingarena.protocol.driver.connection import DriverProcessConnection, DRIVER_PROCESS_CHANNEL, DRIVER_QUEUE
from turingarena.protocol.driver.engine import InterfaceEngine
from turingarena.protocol.exceptions import CommunicationBroken
from turingarena.protocol.module import load_interface_definition
from turingarena.sandbox.client import SandboxProcessClient

logger = logging.getLogger(__name__)


class StopServer(Exception):
    pass


class DriverServer:
    def __init__(self, directory):
        self.boundary = PipeBoundary(directory)
        self.boundary.create_queue(DRIVER_QUEUE)

    # FIXME: lot of code is shared with SandboxServer
    def handle_request(self, sandbox_process_dir, interface):
        if not sandbox_process_dir:
            raise StopServer

        logger.debug(f"handling sandbox request for {sandbox_process_dir}, {interface}")

        driver_process_dir = None

        def run():
            nonlocal driver_process_dir
            with tempfile.TemporaryDirectory(
                    prefix="turingarena_driver_process_",
            ) as driver_process_dir:
                logger.debug(f"created driver process directory {driver_process_dir}")
                # executed in main thread
                process_server = DriverProcessServer(
                    sandbox_process_dir=sandbox_process_dir,
                    interface=interface,
                    driver_process_dir=driver_process_dir
                )
                yield
                # executed in child thread
                logger.debug(f"running driver process server")
                process_server.run()

        handler = run()
        next(handler)
        assert driver_process_dir is not None
        Thread(target=lambda: [x for x in handler]).start()
        return dict(
            driver_process_dir=driver_process_dir,
        )

    def run(self):
        while True:
            logger.debug("waiting for driver requests...")
            try:
                self.boundary.handle_request(DRIVER_QUEUE, self.handle_request)
            except StopServer:
                break

    def stop(self):
        self.boundary.send_empty_request(DRIVER_QUEUE)


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
