import logging
import tempfile
import threading
from threading import Thread

from turingarena.pipeboundary import PipeBoundarySide
from turingarena.sandbox.connection import SandboxProcessBoundary, SandboxProcessWaitBarrier
from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.sandbox.executables import load_executable

logger = logging.getLogger(__name__)


class SandboxException(Exception):
    pass


class SandboxServer:
    def __init__(self, connection):
        self.connection = connection
        self.response_barrier = threading.Barrier(2)

    def serve_one(self, executable):
        with tempfile.TemporaryDirectory(
                prefix="turingarena_sandbox_process_",
        ) as sandbox_dir:
            process_server = SandboxProcessServer(executable=executable, sandbox_dir=sandbox_dir)
            print(sandbox_dir, file=self.connection.response, flush=True)
            self.response_barrier.wait()
            process_server.run()

    def run(self):
        while True:
            line = self.connection.request.readline()
            if not line: break
            algorithm_dir, = line.splitlines()
            executable = load_executable(algorithm_dir)
            threading.Thread(target=lambda: self.serve_one(executable)).start()
            self.response_barrier.wait()


class SandboxProcessServer:
    def __init__(self, *, sandbox_dir, executable):
        self.executable = executable

        logger.debug("sandbox folder: %s", sandbox_dir)

        self.boundary = SandboxProcessBoundary(sandbox_dir)
        self.boundary.init()

        self.wait_barrier = SandboxProcessWaitBarrier(sandbox_dir)
        self.wait_barrier.init()

    def run(self):
        wait_thread = None
        with self.boundary.connect(side=PipeBoundarySide.SERVER) as connection:
            try:
                with self.executable.run(connection):
                    wait_thread = Thread(target=self.wait_for_wait_pipe)
                    wait_thread.start()
            except AlgorithmRuntimeError as e:
                logger.exception(e)
                # FIXME: connection.error_pipe.write(str(e))
        if wait_thread:
            wait_thread.join()

    def wait_for_wait_pipe(self):
        with self.wait_barrier.connect(side=PipeBoundarySide.SERVER):
            pass
        logger.debug("wait barrier reached, terminating...")
