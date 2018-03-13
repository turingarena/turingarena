import logging
from abc import abstractmethod
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

    @abstractmethod
    def get_queue_descriptor(self):
        pass

    @abstractmethod
    def create_child_server(self, child_server_dir, **request_payloads):
        pass

    @abstractmethod
    def run_child_server(self, child_server):
        pass

    @abstractmethod
    def create_response(self, child_server_dir):
        pass

    def run(self):
        while True:
            try:
                self.boundary.handle_request(
                    self.get_queue_descriptor(),
                    self.handle_request,
                )
            except StopMetaServer:
                break

    def _run_child_server(self, child_server, child_server_dir):
        try:
            self.run_child_server(child_server)
        finally:
            child_server_dir.cleanup()

    def handle_request(self, **request_payloads):
        self.handle_stop_request(request_payloads)

        child_server_dir = TemporaryDirectory(dir="/tmp")
        child_server = self.create_child_server(
            child_server_dir.name, **request_payloads
        )

        Thread(target=lambda: self._run_child_server(child_server, child_server_dir)).start()
        return self.create_response(child_server_dir.name)

    def handle_stop_request(self, request_payloads):
        if any(request_payloads.values()): return
        raise StopMetaServer

    def stop(self):
        self.boundary.send_empty_request(self.get_queue_descriptor())
