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
            plumber = Plumber(interface=self.interface, process=process)
            with plumber.connect() as connection:
                yield connection


class PlumberException(Exception):
    pass


class Plumber:
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
                    "plumber",
                    self.interface.name,
                    self.process.sandbox_dir,
                ],
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
            stack.enter_context(plumber_process)
            plumber_dir = plumber_process.stdout.readline().strip()

            assert os.path.isdir(plumber_dir)
            yield PlumberConnection(
                request_pipe=stack.enter_context(open(plumber_dir + "/plumbing_request.pipe", "w")),
                response_pipe=stack.enter_context(open(plumber_dir + "/plumbing_response.pipe")),
            )


class PlumberConnection:
    def __init__(self, *, request_pipe, response_pipe):
        self.request_pipe = request_pipe
        self.response_pipe = response_pipe
