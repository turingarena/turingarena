import logging
import tempfile
from threading import Thread

from turingarena.pipeboundary import PipeBoundarySide, PipeBoundary
from turingarena.sandbox.connection import SandboxProcessConnection, SANDBOX_PROCESS_CHANNEL, \
    SANDBOX_WAIT_BARRIER, SANDBOX_QUEUE
from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.sandbox.executables import load_executable

logger = logging.getLogger(__name__)


class SandboxException(Exception):
    pass


class SandboxServer:
    def __init__(self, directory):
        self.boundary = PipeBoundary(directory)
        self.boundary.create_queue(SANDBOX_QUEUE)

    def handle_request(self, algorithm_dir):
        if not algorithm_dir:
            raise Exception("stopping sandbox server")

        logger.debug(f"handling sandbox request for {algorithm_dir}")
        executable = load_executable(algorithm_dir)

        sandbox_process_dir = None

        def run():
            nonlocal sandbox_process_dir
            with tempfile.TemporaryDirectory(
                    prefix="turingarena_sandbox_process_",
            ) as sandbox_process_dir:
                logger.debug(f"created sandbox process directory {sandbox_process_dir}")
                # executed in main thread
                process_server = SandboxProcessServer(executable=executable, sandbox_dir=sandbox_process_dir)
                yield
                # executed in child thread
                logger.debug(f"running sandbox process server")
                process_server.run()

        handler = run()
        next(handler)
        assert sandbox_process_dir is not None
        Thread(target=lambda: [x for x in handler]).start()
        return dict(
            sandbox_process_dir=sandbox_process_dir,
        )

    def run(self):
        while True:
            logger.debug("waiting for sandbox requests...")
            self.boundary.handle_request(SANDBOX_QUEUE, self.handle_request)

    def stop(self):
        self.boundary.send_request(SANDBOX_QUEUE, algorithm_dir="")


class SandboxProcessServer:
    def __init__(self, *, sandbox_dir, executable):
        self.executable = executable

        logger.debug("sandbox folder: %s", sandbox_dir)

        self.boundary = PipeBoundary(sandbox_dir)
        self.boundary.create_channel(SANDBOX_PROCESS_CHANNEL)
        self.boundary.create_channel(SANDBOX_WAIT_BARRIER)

    def run(self):
        wait_thread = None
        with self.boundary.open_channel(SANDBOX_PROCESS_CHANNEL, PipeBoundarySide.SERVER) as pipes:
            connection = SandboxProcessConnection(**pipes)
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
        with self.boundary.open_channel(SANDBOX_WAIT_BARRIER, PipeBoundarySide.SERVER):
            pass
        logger.debug("wait barrier reached, terminating...")
