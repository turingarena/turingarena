import logging
import threading
from contextlib import ExitStack, contextmanager
from functools import lru_cache
from tempfile import TemporaryDirectory

from turingarena.algorithm import Algorithm
from turingarena.driver.connection import DRIVER_PROCESS_CHANNEL, DriverProcessConnection, SANDBOX_QUEUE, \
    SANDBOX_PROCESS_CHANNEL, SANDBOX_REQUEST_QUEUE, SandboxProcessConnection
from turingarena.pipeboundary import PipeBoundarySide, PipeBoundary
from turingarena.driver.client import SandboxProcessClient
from turingarena_impl.driver.interface.execution import NodeExecutionContext
from turingarena_impl.driver.interface.interface import InterfaceDefinition
from turingarena_impl.driver.language import Language
from turingarena_impl.driver.sandbox.process import CompilationFailedProcess
from turingarena_impl.driver.source import AlgorithmSource, CompilationFailed
from turingarena_impl.metaserver import MetaServer

logger = logging.getLogger(__name__)


class SandboxException(Exception):
    pass


class SandboxServer(MetaServer):
    def get_queue_descriptor(self):
        return SANDBOX_QUEUE

    @contextmanager
    def run_child_server(self, child_server_dir, *, language_name, source_path, interface_path):
        logger.debug("Running sandbox process (server)...")
        algorithm = Algorithm(language_name=language_name, source_path=source_path, interface_path=interface_path)
        server = SandboxProcessServer(
            algorithm=algorithm,
            sandbox_dir=child_server_dir,
            meta_server=self,
        )
        yield
        server.run()

    def create_response(self, child_server_dir):
        return dict(sandbox_process_dir=child_server_dir)

    @lru_cache(maxsize=None)
    def compile_algorithm(self, algorithm):
        if algorithm.language_name is not None:
            language = Language.from_name(algorithm.language_name)
        else:
            language = None
        interface = InterfaceDefinition.load(algorithm.interface_path)
        source = AlgorithmSource.load(
            algorithm.source_path,
            interface=interface,
            language=language,
        )
        try:
            with ExitStack() as exit:
                compilation_dir = exit.enter_context(TemporaryDirectory(prefix="turingarena_"))
                source.compile(compilation_dir)
                # if everything went ok, keep the temporary dir until we stop
                self.exit_stack.push(exit.pop_all())
        except CompilationFailed:
            return source, None
        else:
            return source, compilation_dir


class SandboxProcessServer:
    def __init__(self, *, sandbox_dir, algorithm, meta_server):
        logger.debug("Creating SandboxProcessServer...")
        self.algorithm = algorithm
        self.meta_server = meta_server

        self.boundary = PipeBoundary(sandbox_dir)
        self.boundary.create_channel(SANDBOX_PROCESS_CHANNEL)
        self.boundary.create_queue(SANDBOX_REQUEST_QUEUE)
        self.boundary.create_channel(DRIVER_PROCESS_CHANNEL)

        self.interface = InterfaceDefinition.load(algorithm.interface_path)

        self.done = False
        self.process = None

        self.process_exit_stack = ExitStack()

    def run(self):
        with self.process_exit_stack as stack:
            sandbox_connection = self.start_process_and_connect()

            pipes = stack.enter_context(self.boundary.open_channel(DRIVER_PROCESS_CHANNEL, PipeBoundarySide.SERVER))
            driver_connection = DriverProcessConnection(**pipes)

            context = NodeExecutionContext(
                bindings={},
                phase=None,
                direction=None,
                process=self.process,
                driver_connection=driver_connection,
                sandbox_connection=sandbox_connection,
            )
            self.interface.run_driver(context)

        logger.debug("process terminated")

    def start_process_and_connect(self):
        thread = threading.Thread(target=self._do_start_process)
        thread.start()
        logger.debug("connecting to process...")
        sandbox_process_client = SandboxProcessClient(self.boundary.directory)
        sandbox_connection = self.process_exit_stack.enter_context(
            sandbox_process_client.connect()
        )
        thread.join()
        return sandbox_connection

    def _do_start_process(self):
        logger.debug("starting process...")

        with self.boundary.open_channel(SANDBOX_PROCESS_CHANNEL, PipeBoundarySide.SERVER) as pipes:
            source, compilation_dir = self.meta_server.compile_algorithm(self.algorithm)
            connection = SandboxProcessConnection(**pipes)
            if compilation_dir:
                self.process = self.process_exit_stack.enter_context(
                    source.run(compilation_dir, connection)
                )
            else:
                self.process = CompilationFailedProcess()

    def handle_requests(self):
        while not self.done:
            logger.debug("handling requests...")
            self.boundary.handle_request(
                SANDBOX_REQUEST_QUEUE,
                self.handle_request,
            )

    def handle_request(self, *, wait):
        logger.debug(f"get_info(wait={wait})")

        assert not self.done
        assert wait in ("0", "1")

        info = self.process.get_status(wait=bool(int(wait)))
        logger.debug(f"Process info = {info}")

        if wait == "1":
            self.done = True

        return info.to_payloads()
