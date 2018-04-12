import logging
from contextlib import ExitStack, contextmanager

from turingarena.metaserver import MetaServer
from turingarena.pipeboundary import PipeBoundarySide, PipeBoundary
from turingarena.sandbox.algorithm import CompiledAlgorithm
from turingarena.sandbox.connection import SandboxProcessConnection, SANDBOX_PROCESS_CHANNEL, \
    SANDBOX_QUEUE, SANDBOX_REQUEST_QUEUE
from turingarena.sandbox.executable import AlgorithmExecutable

logger = logging.getLogger(__name__)


class SandboxException(Exception):
    pass


class SandboxServer(MetaServer):
    def get_queue_descriptor(self):
        return SANDBOX_QUEUE

    @contextmanager
    def run_child_server(self, child_server_dir, *, language_name, source_name, interface_name):
        with CompiledAlgorithm.load(
                source_name=source_name,
                interface_name=interface_name,
                language_name=language_name
        ) as algo:
            executable = AlgorithmExecutable.load(algo.algorithm_dir)
            server = SandboxProcessServer(
                executable=executable,
                sandbox_dir=child_server_dir,
            )
            yield
            server.run()

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

        logger.debug("process terminated")

    def handle_request(self, *, wait):
        logger.debug(f"get_info(wait={wait})")

        assert not self.done
        assert wait in ("0", "1")

        info = self.process.get_status(wait_termination=bool(int(wait)))

        time_usage = info.time_usage
        memory_usage = info.memory_usage
        logger.debug(f"Process info = {info}")

        if wait == "1":
            self.done = True
            self.process = None

        return {
            "error": info.error,
            "time_usage": str(time_usage),
            "memory_usage": str(memory_usage),
        }
