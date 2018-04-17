import logging
import threading
from abc import abstractmethod
from contextlib import ExitStack, contextmanager
from tempfile import TemporaryDirectory
from threading import Thread

from turingarena.pipeboundary import PipeBoundary

logger = logging.getLogger(__name__)


class StopMetaServer(Exception):
    pass


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
            meta_server_thread = threading.Thread(target=meta_server.do_run)
            meta_server_thread.start()
            yield boundary_dir
            meta_server.stop()
            meta_server_thread.join()

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
        while True:
            try:
                self.boundary.handle_request(
                    self.get_queue_descriptor(),
                    self.handle_request,
                )
            except StopMetaServer:
                break
        self.exit_stack.close()

    def do_run_child(self, stack, child_server_dir):
        try:
            stack.close()
        finally:
            child_server_dir.cleanup()

    def handle_request(self, **request_payloads):
        self.handle_stop_request(request_payloads)

        child_server_dir = TemporaryDirectory(dir="/tmp")

        stack = ExitStack()
        stack.enter_context(
            self.run_child_server(child_server_dir.name, **request_payloads)
        )
        Thread(target=lambda: self.do_run_child(stack, child_server_dir)).start()
        return self.create_response(child_server_dir.name)

    def handle_stop_request(self, request_payloads):
        if any(request_payloads.values()): return
        raise StopMetaServer

    def stop(self):
        self.boundary.send_empty_request(self.get_queue_descriptor())
