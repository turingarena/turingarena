import logging
import os
import subprocess
from contextlib import contextmanager, ExitStack

from turingarena.cli.loggerinit import init_logger
from turingarena.common import ImmutableObject

logger = logging.getLogger(__name__)

init_logger()


class SandboxException(Exception):
    pass


class SandboxClient:
    @contextmanager
    def run(self, algorithm_dir):
        logger.debug("starting sandbox process")
        with subprocess.Popen(
                ["turingarena-sandbox", algorithm_dir],
                stdout=subprocess.PIPE,
                universal_newlines=True,
        ) as server_process:
            sandbox_dir = server_process.stdout.readline().strip()
            logger.info("connected to sandbox at {}".format(sandbox_dir))

            try:
                yield SandboxProcessClient(sandbox_dir)
            except Exception as e:
                logger.exception(e)
                raise

            logger.debug("waiting sandbox server process")


class SandboxProcessClient:
    def __init__(self, sandbox_dir):
        assert os.path.isdir(sandbox_dir)
        self.sandbox_dir = sandbox_dir
        self.downward_pipe_name = os.path.join(self.sandbox_dir, "downward.pipe")
        self.upward_pipe_name = os.path.join(self.sandbox_dir, "upward.pipe")
        self.wait_pipe_name = os.path.join(self.sandbox_dir, "wait.pipe")

    @contextmanager
    def connect(self):
        logger.debug("connecting to process...")
        try:
            with ExitStack() as stack:
                logger.debug("opening downward pipe...")
                downward_pipe = stack.enter_context(open(self.downward_pipe_name, "w"))
                logger.debug("opening upward pipe...")
                upward_pipe = stack.enter_context(open(self.upward_pipe_name))
                connection = SandboxConnection(
                    downward_pipe=downward_pipe,
                    upward_pipe=upward_pipe,
                )
                logger.debug("connected to process")
                yield connection
        except Exception as e:
            logger.exception(e)
            raise
        finally:
            logger.debug("opening wait pipe")
            with open(self.wait_pipe_name):
                pass


class SandboxConnection(ImmutableObject):
    __slots__ = ["downward_pipe", "upward_pipe"]
