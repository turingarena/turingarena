import logging
import multiprocessing
import shutil
import signal
import tempfile
import threading
from abc import abstractmethod
from contextlib import ExitStack, contextmanager
from tempfile import TemporaryDirectory

from turingarena.pipeboundary import PipeBoundary

logger = logging.getLogger(__name__)


class MetaServer:
    """
    Implements a server that starts child servers.

    This class listens on a synchronous queue:
    it reads the parameters for the server to start,
    starts the child server in a new thread, listening in a temporary directory,
    writes the location of the temporary directory,
    and deletes the temporary directory when the child server stops.
    """

    def __init__(self, directory):
        self.boundary = PipeBoundary(directory)
        self.boundary.create_queue(self.get_queue_descriptor())
        self.exit_stack = ExitStack()

    @classmethod
    @contextmanager
    def run(cls):
        with TemporaryDirectory(dir="/tmp", prefix="turingarena_metaserver_") as boundary_dir:
            meta_server = cls(boundary_dir)
            process = multiprocessing.Process(target=meta_server.do_run)
            process.start()
            try:
                yield boundary_dir
            finally:
                assert process.is_alive()
                process.terminate()
                process.join()

    @abstractmethod
    def get_queue_descriptor(self):
        pass

    @abstractmethod
    def run_child_server(self, child_server_dir, **request_payloads):
        pass

    @abstractmethod
    def create_response(self, child_server_dir):
        pass

    def do_run(self):
        stopped = False

        def handler(signum, frame):
            nonlocal stopped

            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            stopped = True
            raise SystemExit

        signal.signal(signal.SIGTERM, handler)

        try:
            while True:
                self.boundary.handle_request(
                    self.get_queue_descriptor(),
                    self.handle_request,
                )
        except SystemExit:
            logger.info("Meta-server terminating")
            raise
        except:
            logger.exception("Exception in meta-server loop")
        finally:
            self.exit_stack.close()
            if not stopped:
                logger.info("Meta-server waiting for SIGTERM")
                signal.sigwait([signal.SIGTERM])
                logger.info("Meta-server terminated (exception)")

    @contextmanager
    def child_finalizer(self):
        try:
            yield
        except Exception:
            logger.exception("Exception in child server.")

    def handle_request(self, **request_payloads):
        child_stack = ExitStack()

        # do not use TemporaryDirectory since it has a finalizer
        child_server_dir = tempfile.mkdtemp()

        def cleanup():
            shutil.rmtree(child_server_dir, ignore_errors=True)

        self.exit_stack.callback(cleanup)

        child_stack.enter_context(self.child_finalizer())
        child_stack.callback(cleanup)
        child_stack.enter_context(
            self.run_child_server(child_server_dir, **request_payloads)
        )
        thread = threading.Thread(target=child_stack.close)

        thread.start()
        return self.create_response(child_server_dir)
