import logging
import os
import sys
import tempfile
from contextlib import ExitStack
from threading import Thread

from turingarena.sandbox.client import ProcessConnection
from turingarena.sandbox.executables import load_executable

logger = logging.getLogger(__name__)


class SandboxException(Exception):
    pass


class SandboxProcess:
    def __init__(self, *, sandbox_dir, executable):
        self.executable = executable
        self.sandbox_dir = sandbox_dir

        self.downward_pipe_name = os.path.join(sandbox_dir, "downward.pipe")
        self.upward_pipe_name = os.path.join(sandbox_dir, "upward.pipe")
        self.error_pipe_name = os.path.join(sandbox_dir, "error.pipe")
        self.wait_pipe_name = os.path.join(sandbox_dir, "wait.pipe")

        self.os_process = None

        logger.debug("sandbox folder: %s", sandbox_dir)

        logger.debug("creating pipes...")
        os.mkfifo(self.downward_pipe_name)
        os.mkfifo(self.upward_pipe_name)
        os.mkfifo(self.error_pipe_name)
        os.mkfifo(self.wait_pipe_name)
        logger.debug("pipes created")

        self.spawn_thread = Thread(target=self.spawn)
        self.wait_thread = Thread(target=self.wait)

        print(self.sandbox_dir)
        sys.stdout.close()

        self.run()

    def run(self):
        self.wait_thread.start()
        self.spawn_thread.start()

        self.wait_thread.join()
        self.spawn_thread.join()

        if self.os_process is not None:
            self.os_process.kill()
            self.os_process.wait()

    def spawn(self):
        with ExitStack() as stack:
            logger.debug("opening downward pipe...")
            downward_pipe = stack.enter_context(open(self.downward_pipe_name, "r"))
            logger.debug("opening upward pipe...")
            upward_pipe = stack.enter_context(open(self.upward_pipe_name, "w"))
            logger.debug("opening error pipe...")
            error_pipe = stack.enter_context(open(self.error_pipe_name, "w"))
            logger.debug("pipes opened")

            connection = ProcessConnection(
                downward_pipe=downward_pipe,
                upward_pipe=upward_pipe,
                error_pipe=error_pipe,
            )

            self.os_process = self.executable.start_os_process(connection)

    def wait(self):
        logger.debug("opening wait pipe...")
        with open(self.wait_pipe_name, "w"):
            pass
        logger.debug("wait pipe opened, terminating...")


def sandbox_run(algorithm_dir):
    prefix = "turingarena_sandbox_"

    executable = load_executable(algorithm_dir)
    with tempfile.TemporaryDirectory(prefix=prefix) as sandbox_dir:
        SandboxProcess(executable=executable, sandbox_dir=sandbox_dir)
