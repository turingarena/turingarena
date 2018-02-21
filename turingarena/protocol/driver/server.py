import logging
import os
import sys
import tempfile
from contextlib import ExitStack

from turingarena.protocol.connection import DriverConnection
from turingarena.protocol.exceptions import CommunicationBroken
from turingarena.protocol.module import ProtocolModule
from turingarena.protocol.driver.engine import InterfaceEngine
from turingarena.sandbox.client import Process

logger = logging.getLogger(__name__)


class DriverServer:
    def __init__(self, *, protocol_name, interface_name, sandbox_dir):
        self.protocol_definition = ProtocolModule(protocol_name).load_definition()
        self.interface = self.protocol_definition.body.scope.interfaces[interface_name]

        self.main = self.interface.body.scope.main["main"]

        with ExitStack() as stack:
            prefix = "turingarena_driver_"
            driver_dir = stack.enter_context(tempfile.TemporaryDirectory(prefix=prefix))

            request_pipe_name = os.path.join(driver_dir, "driver_request.pipe")
            response_pipe_name = os.path.join(driver_dir, "driver_response.pipe")
            error_pipe_name = os.path.join(driver_dir, "error.pipe")

            logger.debug("creating request/response pipes...")
            os.mkfifo(request_pipe_name)
            os.mkfifo(response_pipe_name)
            os.mkfifo(error_pipe_name)

            print(driver_dir)
            sys.stdout.close()

            logger.debug("opening request pipe...")
            request_pipe = stack.enter_context(open(request_pipe_name))
            logger.debug("opening response pipe...")
            response_pipe = stack.enter_context(open(response_pipe_name, "w"))
            logger.debug("opening error pipe...")
            error_pipe = stack.enter_context(open(error_pipe_name, "w"))
            logger.debug("pipes opened")

            self.driver_connection = DriverConnection(
                request_pipe=request_pipe,
                response_pipe=response_pipe,
                error_pipe=error_pipe,
            )

            logger.debug("connecting to process...")
            self.process_connection = stack.enter_context(Process(sandbox_dir).connect())
            logger.debug("connected")

            self.engine = InterfaceEngine(
                process_connection=self.process_connection,
                driver_connection=self.driver_connection,
                interface=self.interface
            )

            try:
                self.engine.run()
            except CommunicationBroken:
                logger.warning(f"communication with process broken")
                error = self.process_connection.error_pipe.read()
                self.driver_connection.error_pipe.write(error)
