import logging
import sys
from contextlib import ExitStack

import os
import tempfile

from turingarena.protocol.module import load_protocol
from turingarena.protocol.connection import ProxyConnection
from turingarena.protocol.server.engine import InterfaceEngine
from turingarena.sandbox.client import Process

logger = logging.getLogger(__name__)


class ProxyServer:
    def __init__(self, *, protocol_name, interface_name, sandbox_dir):
        protocol = load_protocol(protocol_name)
        self.protocol = protocol
        self.interface = protocol.body.scope.interfaces[interface_name]

        self.main = self.interface.body.scope.main["main"]

        with ExitStack() as stack:
            prefix = "turingarena_proxy"
            proxy_dir = stack.enter_context(tempfile.TemporaryDirectory(prefix=prefix))

            request_pipe_name = os.path.join(proxy_dir, "proxy_request.pipe")
            response_pipe_name = os.path.join(proxy_dir, "proxy_response.pipe")

            logger.debug("creating request/response pipes...")
            os.mkfifo(request_pipe_name)
            os.mkfifo(response_pipe_name)

            print(proxy_dir)
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

            self.engine = InterfaceEngine(
                process_connection=self.process_connection,
                proxy_connection=self.proxy_connection,
                interface=self.interface
            )

            self.engine.run()
