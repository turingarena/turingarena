import logging
import os

import subprocess
from contextlib import contextmanager, ExitStack

logger = logging.getLogger(__name__)


class Interface:
    def __init__(self, package_name, name):
        self.package_name = package_name
        self.name = name


class Implementation:
    def __init__(self, *, interface, algorithm):
        self.interface = interface
        self.algorithm = algorithm

    @contextmanager
    def run(self):
        sandbox = self.algorithm.sandbox()
        with sandbox.run() as process:
            plumber = ProxyClient(interface=self.interface, process=process)
            with plumber.connect() as connection:
                yield connection


class ProxyClient:
    def __init__(self, *, interface, process):
        self.interface = interface
        self.process = process

    @contextmanager
    def connect(self):
        with ExitStack() as stack:
            plumber_process = subprocess.Popen(
                [
                    "turingarena",
                    "protocol",
                    "-p", self.interface.package_name,
                    "server",
                    self.interface.name,
                    self.process.sandbox_dir,
                ],
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
