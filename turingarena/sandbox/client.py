import logging
import os

import subprocess

logger = logging.getLogger(__name__)


class SandboxException(Exception):
    pass


class Algorithm:
    def __init__(self, name):
        self.name = name

    def create_process(self):
        return Process(self.name)


class Process:
    def __init__(self, algorithm_name):
        self.algorithm_name = algorithm_name

        self.sandbox = subprocess.Popen(
            ["turingarena", "sandbox", "run", algorithm_name],
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        self.sandbox_dir = self.sandbox.stdout.readline().strip()

        assert os.path.isdir(self.sandbox_dir)
        logger.info("connected to sandbox at {}".format(self.sandbox_dir))

        self.downward_pipe_name = self.sandbox_dir + "/downward.pipe"
        self.downward_pipe = None
        self.upward_pipe_name = self.sandbox_dir + "/upward.pipe"
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

    def attach_downward(self):
        self.downward_pipe = open(self.downward_pipe_name, "w", buffering=1)
        logger.debug("successfully opened downward pipe")

    def attach_upward(self):
        self.upward_pipe = open(self.upward_pipe_name, "r")
        logger.debug("successfully opened upward pipe")

    def wait(self):
        logger.debug("Waiting process")
        self.request("wait")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wait()
        self.sandbox.wait()
