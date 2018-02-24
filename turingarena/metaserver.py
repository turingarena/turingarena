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
            logger.debug("waiting for requests for child servers...")
            try:
                self.boundary.handle_request(
                    self.get_queue_descriptor(),
                    self.handle_request,
                )
            except StopMetaServer:
                break

    def handle_request(self, **request_payloads):
        if not all(request_payloads.values()):
            # either all parameters are present, or none is
            assert not any(request_payloads.values())
            raise StopMetaServer

        logger.debug("handling requests for a child server...")

        child_server_dir = None

        def run():
            nonlocal child_server_dir
            with TemporaryDirectory() as child_server_dir:
                logger.debug(f"created child server directory {child_server_dir}")
                # executed in main thread
                child_server = self.create_child_server(
                    child_server_dir, **request_payloads
                )
                yield
                # executed in child thread
                logger.debug(f"running child server")
                self.run_child_server(child_server)

        handler = run()
        next(handler)
        assert child_server_dir is not None
        Thread(target=lambda: [x for x in handler]).start()
        return self.create_response(child_server_dir)

    def stop(self):
        self.boundary.send_empty_request(self.get_queue_descriptor())
