import logging
from threading import Thread

from turingarena.metaserver import MetaServer
from turingarena.pipeboundary import PipeBoundarySide, PipeBoundary
from turingarena.sandbox.connection import SandboxProcessConnection, SANDBOX_PROCESS_CHANNEL, \
    SANDBOX_WAIT_BARRIER, SANDBOX_QUEUE
from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.sandbox.executables import load_executable

logger = logging.getLogger(__name__)


class SandboxException(Exception):
    pass


class SandboxServer(MetaServer):
    def get_queue_descriptor(self):
        return SANDBOX_QUEUE

    def create_child_server(self, child_server_dir, *, algorithm_dir):
        executable = load_executable(algorithm_dir)
        return SandboxProcessServer(executable=executable, sandbox_dir=child_server_dir)

    def run_child_server(self, child_server):
        child_server.run()

    def create_response(self, child_server_dir):
        return dict(sandbox_process_dir=child_server_dir)


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
