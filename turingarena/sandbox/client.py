import logging
import os

import subprocess
from contextlib import AbstractContextManager

logger = logging.getLogger(__name__)


class SandboxException(Exception):
    pass


class Algorithm:
    def __init__(self, name):
        self.name = name

    def create_process(self):
        return Process(self.name)


class Process(AbstractContextManager):
    def __init__(self, algorithm_name):
        self.algorithm_name = algorithm_name

        sandbox = subprocess.Popen(
            ["turingarena", "sandbox", "run", algorithm_name],
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        self.sandbox_dir = sandbox.stdout.readline().strip()

        self.downward_pipe = None
        self.upward_pipe = None

    def request(self, *args):
        with open(self.sandbox_dir + "/control_request.pipe", "w") as p:
            for a in args:
                print(a, file=p)
        with open(self.sandbox_dir + "/control_response.pipe", "r") as p:
            result = int(p.readline().strip())
            if result:
                raise SandboxException

    def start(self):
        logger.debug("Starting process")
        self.request("start")

        self.downward_pipe = open(self.sandbox_dir + "/downward.pipe", "w", buffering=1)
        self.upward_pipe = open(self.sandbox_dir + "/upward.pipe", "r")

        logger.debug("successfully opened pipes")

    def wait(self):
        logger.debug("Waiting process")
        self.request("wait")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wait()
