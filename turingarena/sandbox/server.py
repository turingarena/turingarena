import logging
import os
import sys
import tempfile
from threading import Thread

from turingarena.cli.loggerinit import init_logger
from turingarena.pipeboundary import PipeBoundarySide
from turingarena.sandbox.connection import SandboxProcessBoundary
from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.sandbox.executables import load_executable

logger = logging.getLogger(__name__)

init_logger()


class SandboxException(Exception):
    pass


class SandboxProcessServer:
    def __init__(self, *, sandbox_dir, executable):
        self.executable = executable
        self.sandbox_dir = sandbox_dir  # FIXME: drop this field in favor of 'boundary'

        logger.debug("sandbox folder: %s", sandbox_dir)

        self.boundary = SandboxProcessBoundary(directory=sandbox_dir)
        self.boundary.init()

        self.wait_pipe_name = os.path.join(sandbox_dir, "wait.pipe")
        os.mkfifo(self.wait_pipe_name)

        print(self.sandbox_dir)
        sys.stdout.close()

        self.run()

    def run(self):
        wait_thread = None
        with self.boundary.connect(side=PipeBoundarySide.SERVER) as connection:
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


def sandbox_run(algorithm_dir):
    prefix = "turingarena_sandbox_"

    executable = load_executable(algorithm_dir)
    with tempfile.TemporaryDirectory(prefix=prefix) as sandbox_dir:
        SandboxProcessServer(executable=executable, sandbox_dir=sandbox_dir)
