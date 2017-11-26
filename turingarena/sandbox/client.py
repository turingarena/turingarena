import logging
import subprocess
from contextlib import contextmanager, ExitStack

import os

from turingarena.cli.loggerinit import init_logger

logger = logging.getLogger(__name__)

init_logger()


class SandboxException(Exception):
    pass


class Algorithm:
    def __init__(self, name):
        self.name = name

    def sandbox(self):
        return SandboxClient(self.name)


class SandboxClient:
    def __init__(self, algorithm_name):
        logger.debug("creating a sandbox client")
        self.algorithm_name = algorithm_name

    @contextmanager
    def run(self):
        logger.debug("starting sandbox process")
        with subprocess.Popen(
                ["turingarena", "sandbox", "run", self.algorithm_name],
                stdout=subprocess.PIPE,
                universal_newlines=True,
        ) as sandbox_process:
            sandbox_dir = sandbox_process.stdout.readline().strip()
            logger.info("connected to sandbox at {}".format(sandbox_dir))

            try:
                yield Process(sandbox_dir)
            except Exception as e:
                logger.exception(e)
                raise

            logger.debug("waiting sandbox process")


class Process:
    def __init__(self, sandbox_dir):
        assert os.path.isdir(sandbox_dir)
        self.sandbox_dir = sandbox_dir
        self.downward_pipe_name = self.sandbox_dir + "/downward.pipe"
        self.upward_pipe_name = self.sandbox_dir + "/upward.pipe"

    def request(self, *args):
        logger.debug("sending request {}...".format(args))
        with open(self.sandbox_dir + "/control_request.pipe", "w") as p:
            for a in args:
                print(a, file=p)
        logger.debug("waiting response...")
        with open(self.sandbox_dir + "/control_response.pipe", "r") as p:
            result = int(p.readline().strip())
            if result:
                raise SandboxException
        logger.debug("response received: {}".format(result))

    def start(self):
        logger.info("starting process")
        self.request("start")

    def kill(self):
        logger.info("killing process")
        self.request("kill")

    def wait(self):
        logger.info("waiting for process")
        self.request("wait")

    @contextmanager
    def connect(self):
        logger.debug("connecting to process...")
        with ExitStack() as stack:
            self.start()
            try:
                logger.debug("opening downward pipe...")
                downward_pipe = stack.enter_context(open(self.downward_pipe_name, "w"))
                logger.debug("opening upward pipe...")
                upward_pipe = stack.enter_context(open(self.upward_pipe_name))
                yield ProcessConnection(downward_pipe=downward_pipe, upward_pipe=upward_pipe)
            except Exception as e:
                logger.exception(e)
                self.kill()
                raise
            finally:
                self.wait()


class ProcessConnection:
    def __init__(self, *, downward_pipe, upward_pipe):
        self.downward_pipe = downward_pipe
        self.upward_pipe = upward_pipe
