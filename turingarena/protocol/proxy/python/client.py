import logging
import os
import subprocess
from contextlib import contextmanager, ExitStack

logger = logging.getLogger(__name__)


class ProxyClient:
    def __init__(self, *, protocol_name, interface_name, process):
        self.protocol_name = protocol_name
        self.interface_name = interface_name
        self.process = process

    @contextmanager
    def connect(self):
        cli = [
            f"turingarena",
            f"protocol",
            f"--name={self.protocol_name}",
            f"server",
            f"--interface={self.interface_name}",
            f"--sandbox={self.process.sandbox_dir}",
        ]
        with ExitStack() as stack:
            logger.debug(f"running {cli}...")
            proxy_process = subprocess.Popen(
                cli,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
            stack.enter_context(proxy_process)
            proxy_dir = proxy_process.stdout.readline().strip()
            logger.debug(f"proxy dir: {proxy_dir}...")

            assert os.path.isdir(proxy_dir)

            logger.debug("opening request pipe...")
            request_pipe = stack.enter_context(open(proxy_dir + "/proxy_request.pipe", "w"))
            logger.debug("opening response pipe...")
            response_pipe = stack.enter_context(open(proxy_dir + "/proxy_response.pipe"))
            logger.debug("proxy connected")

            try:
                yield ProxyConnection(
                    request_pipe=request_pipe,
                    response_pipe=response_pipe,
                )
            except Exception as e:
                logger.exception(e)
                raise

            logger.debug("waiting for proxy server process")


class ProxyConnection:
    def __init__(self, *, request_pipe, response_pipe):
        self.request_pipe = request_pipe
        self.response_pipe = response_pipe
