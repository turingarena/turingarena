import logging
import os
import sys
import tempfile
from contextlib import ExitStack

from turingarena.protocol.plumber import run_porcelain
from turingarena.sandbox.client import Process

logger = logging.getLogger(__name__)


class PlumberServer:
    def __init__(self, *, protocol, interface_name, sandbox_dir):
        prefix = "turingarena_plumber"

        self.protocol = protocol
        [self.interface] = [
            s for s in protocol.statements
            if s.statement_type == "interface"
               and s.name == interface_name
        ]

        with ExitStack() as stack:
            self.plumber_dir = stack.enter_context(tempfile.TemporaryDirectory(prefix=prefix))

            request_pipe_name = os.path.join(self.plumber_dir, "plumbing_request.pipe")
            response_pipe_name = os.path.join(self.plumber_dir, "plumbing_response.pipe")

            logger.debug("creating request/response pipes...")
            os.mkfifo(request_pipe_name)
            os.mkfifo(response_pipe_name)

            print(self.plumber_dir)
            sys.stdout.close()

            logger.debug("opening request pipe...")
            self.request_pipe = stack.enter_context(open(request_pipe_name))
            logger.debug("opening response pipe...")
            self.response_pipe = stack.enter_context(open(response_pipe_name, "w"))
            logger.debug("pipes opened")

            logger.debug("connecting to process...")
            self.connection = stack.enter_context(Process(sandbox_dir).connect())
            logger.debug("connected")

            run_porcelain(self)

    def receive(self):
        logger.debug("receiving request")
        line = self.request_pipe.readline().strip()
        logger.debug("received request '{}'".format(line))
        return line

    def send(self, line):
        logger.debug("sending response '{}'".format(line))
        print(line, file=self.response_pipe)
