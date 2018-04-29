import itertools
import logging
import os
from collections import namedtuple
from contextlib import ExitStack, contextmanager
from enum import Enum

logger = logging.getLogger(__name__)


class PipeBoundarySide(Enum):
    CLIENT = 0
    SERVER = 1


PipeDescriptor = namedtuple("PipeDescriptor", ["filename", "flags"])
PipeChannelDescriptor = namedtuple("PipeChannelDescriptor", ["pipes"])
PipeSynchronousQueueDescriptor = namedtuple("PipeSynchronousQueueDescriptor", [
    "request_pipes", "response_pipes"
])


class PipeBoundary:
    __slots__ = ["directory"]

    def __init__(self, directory):
        assert os.path.isdir(directory)
        self.directory = directory

    def pipe_path(self, descriptor):
        return os.path.join(self.directory, descriptor.filename)

    def create_pipe(self, descriptor):
        path = self.pipe_path(descriptor)
        os.mkfifo(path)

    @contextmanager
    def open_pipe(self, descriptor, side):
        path = self.pipe_path(descriptor)
        flags = descriptor.flags[side.value]
        # logger.debug(f"open({repr(path)}, {repr(flags)})")
        with open(path, flags) as pipe:
            yield pipe

    def create_channel(self, descriptor):
        for pipe in descriptor.pipes.values():
            self.create_pipe(pipe)

    @contextmanager
    def open_channel(self, descriptor, side):
        with ExitStack() as stack:
            yield {
                name: stack.enter_context(self.open_pipe(pipe, side))
                for name, pipe in descriptor.pipes.items()
            }

    def sync_write(self, descriptor, side, payload):
        with self.open_pipe(descriptor, side) as p:
            if payload is not None:
                p.write(payload)

    def sync_read(self, descriptor, side):
        with self.open_pipe(descriptor, side) as p:
            return p.read() or None

    def create_queue(self, descriptor):
        for name, pipe in itertools.chain(
                descriptor.request_pipes.items(),
                descriptor.response_pipes.items(),
        ):
            os.mkfifo(self.pipe_path(pipe))

    def send_empty_request(self, descriptor):
        return self.send_request(descriptor, **{n: None for n in descriptor.request_pipes})

    def send_request(self, descriptor, **request_payloads):
        assert len(descriptor.request_pipes) == len(request_payloads)

        for name, pipe in descriptor.request_pipes.items():
            self.sync_write(pipe, PipeBoundarySide.CLIENT, request_payloads[name])
        response_payloads = {
            name: self.sync_read(pipe, PipeBoundarySide.CLIENT)
            for name, pipe in descriptor.response_pipes.items()
        }
        return response_payloads

    def handle_request(self, descriptor, handler):
        request_payloads = {
            name: self.sync_read(pipe, PipeBoundarySide.SERVER)
            for name, pipe in descriptor.request_pipes.items()
        }
        response_payloads = handler(**request_payloads)
        self._send_payloads(descriptor, response_payloads)

    def _send_payloads(self, descriptor, response_payloads):
        for name, pipe in descriptor.response_pipes.items():
            payload = response_payloads.get(name)
            self.sync_write(pipe, PipeBoundarySide.SERVER, payload)
