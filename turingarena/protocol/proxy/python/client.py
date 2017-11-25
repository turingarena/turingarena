import logging
import subprocess
from contextlib import contextmanager, ExitStack

import os

logger = logging.getLogger(__name__)


class ProxyClient:
    def __init__(self, *, protocol_name, interface_name, process):
        self.protocol_name = protocol_name
        self.interface_name = interface_name
        self.process = process

    @contextmanager
    def connect(self):
        cli = (
            f"turingarena protocol --name {self.protocol_name}"
            f" server"
            f" --interface {self.interface_name}"
            f" --sandbox {self.process.sandbox_dir}"
        )
        with ExitStack() as stack:
            plumber_process = subprocess.Popen(
                cli,
                shell=True,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
            stack.enter_context(plumber_process)
            plumber_dir = plumber_process.stdout.readline().strip()

            assert os.path.isdir(plumber_dir)

            logger.debug("opening request pipe...")
            request_pipe = stack.enter_context(open(plumber_dir + "/plumbing_request.pipe", "w"))
            logger.debug("opening response pipe...")
            response_pipe = stack.enter_context(open(plumber_dir + "/plumbing_response.pipe"))
            logger.debug("connected")

            try:
                yield ProxyConnection(
                    request_pipe=request_pipe,
                    response_pipe=response_pipe,
                )
            except Exception as e:
                logger.exception(e)
                raise

            logger.debug("waiting for plumber process")


class ProxyConnection:
    def __init__(self, *, request_pipe, response_pipe):
        self.request_pipe = request_pipe
        self.response_pipe = response_pipe
