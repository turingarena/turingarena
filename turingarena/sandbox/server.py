import logging
import os
import sys
import tempfile
from contextlib import ExitStack, contextmanager
from threading import Thread

from turingarena.sandbox.client import SandboxConnection
from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.sandbox.executables import load_executable

logger = logging.getLogger(__name__)


class SandboxException(Exception):
    pass


class SandboxProcessServer:
    def __init__(self, *, sandbox_dir, executable):
        self.executable = executable
        self.sandbox_dir = sandbox_dir

        logger.debug("sandbox folder: %s", sandbox_dir)

        self.downward_pipe_name = os.path.join(sandbox_dir, "downward.pipe")
        self.upward_pipe_name = os.path.join(sandbox_dir, "upward.pipe")
        self.wait_pipe_name = os.path.join(sandbox_dir, "wait.pipe")

        self.create_pipes()

        print(self.sandbox_dir)
        sys.stdout.close()

        self.run()

    def run(self):
        wait_thread = None
        with self.open_connection() as connection:
            try:
                with self.executable.run(connection) as p:
                    def wait():
                        self.wait_for_wait_pipe()
                        p.kill()

                    wait_thread = Thread(target=wait)
                    wait_thread.start()
            except AlgorithmRuntimeError as e:
                logger.exception(e)
                # FIXME: connection.error_pipe.write(str(e))
        if wait_thread:
            wait_thread.join()

    def wait_for_wait_pipe(self):
        logger.debug("opening wait pipe...")
        with open(self.wait_pipe_name, "w"):
            pass
        logger.debug("wait pipe opened, terminating...")

    def create_pipes(self):
        logger.debug("creating pipes...")
        os.mkfifo(self.downward_pipe_name)
        os.mkfifo(self.upward_pipe_name)
        os.mkfifo(self.wait_pipe_name)
        logger.debug("pipes created")

    @contextmanager
    def open_connection(self):
        with ExitStack() as stack:
            logger.debug("opening downward pipe...")
            downward_pipe = stack.enter_context(open(self.downward_pipe_name, "r"))
            logger.debug("opening upward pipe...")
            upward_pipe = stack.enter_context(open(self.upward_pipe_name, "w"))
            logger.debug("pipes opened")

            yield SandboxConnection(
                downward_pipe=downward_pipe,
                upward_pipe=upward_pipe,
            )


def sandbox_run(algorithm_dir):
    prefix = "turingarena_sandbox_"

    executable = load_executable(algorithm_dir)
    with tempfile.TemporaryDirectory(prefix=prefix) as sandbox_dir:
        SandboxProcessServer(executable=executable, sandbox_dir=sandbox_dir)
