import logging
import os
import shutil
import tempfile
from contextlib import ExitStack, contextmanager
from tempfile import mkdtemp
from threading import Thread

from turingarena.sandbox.connection import ProcessConnection
from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.sandbox.executables import load_executable

logger = logging.getLogger(__name__)


class SandboxException(Exception):
    pass


class SandboxProcess:
    def __init__(self, *, sandbox_dir, executable):
        self.executable = executable
        self.sandbox_dir = sandbox_dir

        logger.debug("sandbox folder: %s", sandbox_dir)

        self.downward_pipe_name = os.path.join(sandbox_dir, "downward.pipe")
        self.upward_pipe_name = os.path.join(sandbox_dir, "upward.pipe")
        self.error_pipe_name = os.path.join(sandbox_dir, "error.pipe")
        self.wait_pipe_name = os.path.join(sandbox_dir, "wait.pipe")

        self.create_pipes()
        self.waited = False

    def run(self):
        wait_thread = None
        with self.open_connection() as connection:
            try:
                with self.executable.run(connection) as p:
                    def wait():
                        self.wait_for_wait_pipe()
                        self.waited = True
                        p.kill()

                    wait_thread = Thread(target=wait)
                    wait_thread.start()
            except AlgorithmRuntimeError as e:
                logger.exception(e)
                if not self.waited:
                    connection.error_pipe.write(str(e))
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
        os.mkfifo(self.error_pipe_name)
        os.mkfifo(self.wait_pipe_name)
        logger.debug("pipes created")

    @contextmanager
    def open_connection(self):
        with ExitStack() as stack:
            logger.debug("opening downward pipe...")
            downward_pipe = stack.enter_context(open(self.downward_pipe_name, "r"))
            logger.debug("opening upward pipe...")
            upward_pipe = stack.enter_context(open(self.upward_pipe_name, "w"))
            logger.debug("opening error pipe...")
            error_pipe = stack.enter_context(open(self.error_pipe_name, "w"))
            logger.debug("pipes opened")

            yield ProcessConnection(
                downward_pipe=downward_pipe,
                upward_pipe=upward_pipe,
                error_pipe=error_pipe,
            )


class SandboxServer:
    def __init__(self):
        self.server_dir = mkdtemp(prefix="turingarena_sandbox_server_")

        self.request_pipe_name = os.path.join(self.server_dir, "sandbox_server_request.pipe")
        self.response_pipe_name = os.path.join(self.server_dir, "sandbox_server_response.pipe")

        os.mkfifo(self.request_pipe_name)
        os.mkfifo(self.response_pipe_name)

        # FIXME: should not be a daemon thread
        self.thread = Thread(target=self.serve_sandboxes, daemon=True)
        self.thread.start()

    @contextmanager
    def sandbox_run(self, algorithm_dir):
        executable = load_executable(algorithm_dir)

        prefix = "algorithm_"
        with tempfile.TemporaryDirectory(prefix=prefix, dir=self.server_dir) as sandbox_dir:
            process = SandboxProcess(executable=executable, sandbox_dir=sandbox_dir)
            yield sandbox_dir
            process.run()

    def serve_sandboxes(self):
        try:
            while True:
                with open(self.request_pipe_name) as f:
                    algorithm_dir = f.read()
                    if not algorithm_dir:
                        raise Exception("stop")
                with self.sandbox_run(algorithm_dir) as sandbox_dir:
                    with open(self.response_pipe_name, "w") as f:
                        f.write(sandbox_dir)
        finally:
            shutil.rmtree(self.server_dir)
