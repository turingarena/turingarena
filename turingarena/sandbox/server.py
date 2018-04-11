import logging
from contextlib import ExitStack

from turingarena.metaserver import MetaServer
from turingarena.pipeboundary import PipeBoundarySide, PipeBoundary
from turingarena.sandbox.connection import SandboxProcessConnection, SANDBOX_PROCESS_CHANNEL, \
    SANDBOX_QUEUE, SANDBOX_REQUEST_QUEUE
from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.sandbox.executable import AlgorithmExecutable

logger = logging.getLogger(__name__)


class SandboxException(Exception):
    pass


class SandboxServer(MetaServer):
    def get_queue_descriptor(self):
        return SANDBOX_QUEUE

    def create_child_server(self, child_server_dir, *, algorithm_dir):
        executable = AlgorithmExecutable.load(algorithm_dir)
        return SandboxProcessServer(executable=executable, sandbox_dir=child_server_dir)

    def run_child_server(self, child_server):
        child_server.run()

    def create_response(self, child_server_dir):
        return dict(sandbox_process_dir=child_server_dir)


class SandboxProcessServer:
    def __init__(self, *, sandbox_dir, executable):
        self.executable = executable

        self.boundary = PipeBoundary(sandbox_dir)
        self.boundary.create_channel(SANDBOX_PROCESS_CHANNEL)
        self.boundary.create_queue(SANDBOX_REQUEST_QUEUE)

        self.done = False
        self.process = None

        self.process_exit_stack = ExitStack()

    def run(self):
        logger.debug("starting process...")

        with self.boundary.open_channel(SANDBOX_PROCESS_CHANNEL, PipeBoundarySide.SERVER) as pipes:
            connection = SandboxProcessConnection(**pipes)
            self.process = self.process_exit_stack.enter_context(
                self.executable.run(connection)
            )

        logger.debug("process started")

        while not self.done:
            logger.debug("handling requests...")
            self.boundary.handle_request(
                SANDBOX_REQUEST_QUEUE,
                self.handle_request,
            )

    def handle_request(self, *, wait):
        assert not self.done
        assert wait in ("0", "1")

        time_usage = self.executable.get_time_usage(self.process)
        memory_usage = self.executable.get_memory_usage(self.process)

        message = ""
        if wait == "1":
            self.done = True
            self.process = None
            try:
                self.process_exit_stack.close()
            except AlgorithmRuntimeError as e:
                [message] = e.args

        return {
            "error": message,
            "time_usage": str(time_usage),
            "memory_usage": str(memory_usage),
        }
