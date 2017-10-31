import logging
import os
import sys
import tempfile
from contextlib import ExitStack

from turingarena.protocol.proxy.python.client import ProxyConnection
from turingarena.protocol.server.frames import PreflightContext, RunContext, InterfaceEnvironment
from turingarena.sandbox.client import Process

logger = logging.getLogger(__name__)


class PlumberServer:
    def __init__(self, *, protocol, interface_name, sandbox_dir):
        self.protocol = protocol
        self.interface = protocol.body.scope.interfaces[interface_name]

        self.main = self.interface.body.scope.main["main"]

        with ExitStack() as stack:
            prefix = "turingarena_plumber"
            plumber_dir = stack.enter_context(tempfile.TemporaryDirectory(prefix=prefix))

            request_pipe_name = os.path.join(plumber_dir, "plumbing_request.pipe")
            response_pipe_name = os.path.join(plumber_dir, "plumbing_response.pipe")

            logger.debug("creating request/response pipes...")
            os.mkfifo(request_pipe_name)
            os.mkfifo(response_pipe_name)

            print(plumber_dir)
            sys.stdout.close()

            logger.debug("opening request pipe...")
            request_pipe = stack.enter_context(open(request_pipe_name))
            logger.debug("opening response pipe...")
            response_pipe = stack.enter_context(open(response_pipe_name, "w"))
            logger.debug("pipes opened")

            self.proxy_connection = ProxyConnection(
                request_pipe=request_pipe,
                response_pipe=response_pipe,
            )

            logger.debug("connecting to process...")
            self.process_connection = stack.enter_context(Process(sandbox_dir).connect())
            logger.debug("connected")

            environment = InterfaceEnvironment(interface=self.interface)
            self.preflight_context = PreflightContext(
                proxy_connection=self.proxy_connection,
                environment=environment,
                on_advance=lambda: next(self.runner),
            )
            self.run_context = RunContext(
                process_connection=self.process_connection,
                environment=environment,
            )

            self.runner = self.interface.run(context=self.run_context)
            self.interface.preflight(context=self.preflight_context)
