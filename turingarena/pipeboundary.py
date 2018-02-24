import logging
import os
from contextlib import ExitStack
from enum import Enum

from decorator import contextmanager

from turingarena.common import ImmutableObject

logger = logging.getLogger(__name__)


class PipeBoundarySide(Enum):
    CLIENT = 0
    SERVER = 1


class PipeDescriptor(ImmutableObject):
    __slots__ = ["filename", "flags"]

    def __init__(self, filename, flags):
        super().__init__(filename=filename, flags=flags)


class PipeChannelDescriptor(ImmutableObject):
    __slots__ = ["pipes"]


class PipeBoundary(ImmutableObject):
    __slots__ = ["directory"]

    def __init__(self, directory):
        assert os.path.isdir(directory)
        super().__init__(directory=directory)

    def pipe_path(self, descriptor):
        return os.path.join(self.directory, descriptor.filename)

    def create_pipe(self, descriptor):
        path = self.pipe_path(descriptor)
        logger.debug(f"creating pipe {descriptor} ({path})")
        os.mkfifo(path)

    @contextmanager
    def open_pipe(self, descriptor, side):
        path = self.pipe_path(descriptor)
        flags = descriptor.flags[side.value]
        logger.debug(f"opening pipe {descriptor}, side {side}")
        logger.debug(f"open({repr(path)}, {repr(flags)})")
        with open(path, flags) as pipe:
            yield pipe

    def create_channel(self, descriptor):
        logger.debug(f"creating channel {descriptor}")
        for pipe in descriptor.pipes.values():
            self.create_pipe(pipe)

    @contextmanager
    def open_channel(self, descriptor, side):
        logger.debug(f"open channel {descriptor}, side {side}")
        with ExitStack() as stack:
            yield {
                name: stack.enter_context(self.open_pipe(pipe, side))
                for name, pipe in descriptor.pipes.items()
            }
