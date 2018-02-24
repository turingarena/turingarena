import logging
import os
import sys
import tempfile
from contextlib import ExitStack

from turingarena.protocol.driver.connection import DriverProcessConnection
from turingarena.protocol.driver.engine import InterfaceEngine
from turingarena.protocol.exceptions import CommunicationBroken
from turingarena.protocol.module import load_interface_definition
from turingarena.sandbox.client import SandboxProcessClient

logger = logging.getLogger(__name__)


class DriverServer:
    def __init__(self, *, interface, sandbox_dir):
        self.interface_definition = load_interface_definition(interface)

        self.main = self.interface_definition.body.scope.main["main"]

        with ExitStack() as stack:
            prefix = "turingarena_driver_"
            driver_dir = stack.enter_context(tempfile.TemporaryDirectory(prefix=prefix))

            request_pipe_name = os.path.join(driver_dir, "driver_request.pipe")
            response_pipe_name = os.path.join(driver_dir, "driver_response.pipe")

            logger.debug("creating request/response pipes...")
            os.mkfifo(request_pipe_name)
            os.mkfifo(response_pipe_name)

            print(driver_dir)
            sys.stdout.close()

            logger.debug("opening request pipe...")
            request_pipe = stack.enter_context(open(request_pipe_name))
            logger.debug("opening response pipe...")
            response_pipe = stack.enter_context(open(response_pipe_name, "w"))
            logger.debug("pipes opened")

            self.driver_connection = DriverProcessConnection(
                request=request_pipe,
                response=response_pipe,
            )

            logger.debug("connecting to process...")
            self.sandbox_connection = stack.enter_context(SandboxProcessClient(sandbox_dir).connect())
            logger.debug("connected")

            self.engine = InterfaceEngine(
                sandbox_connection=self.sandbox_connection,
                driver_connection=self.driver_connection,
                interface=self.interface_definition
            )

            try:
                self.engine.run()
            except CommunicationBroken as e:
                logger.warning(f"communication with process broken")
                logger.exception(e)
