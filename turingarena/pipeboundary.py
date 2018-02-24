import logging
import os
from contextlib import ExitStack, contextmanager
from enum import Enum

from turingarena.common import ImmutableObject

logger = logging.getLogger(__name__)


class BoundarySide(Enum):
    CLIENT = 0
    SERVER = 1


class PipeBoundary(ImmutableObject):
    __slots__ = ["directory"]

    SERVER = BoundarySide.SERVER
    CLIENT = BoundarySide.CLIENT

    pipe_info = NotImplemented
    create_connection = NotImplemented

    def __init__(self, directory):
        assert os.path.isdir(directory)
        super().__init__(directory=directory)

    def pipe_path(self, name):
        return os.path.join(self.directory, f"{name}.pipe")

    def init(self):
        for name in self.pipe_info:
            path = self.pipe_path(name)
            logger.debug(f"creating pipe {name} ({path})")
            os.mkfifo(path)

    def open_pipe(self, name, side):
        path = self.pipe_path(name)
        flags = self.pipe_info[name][side.value]
        logger.debug(f"opening pipe {name}, side {side} [open({repr(path)}, {repr(flags)})]")
        return open(path, flags)

    @contextmanager
    def connect(self, side):
        logger.debug(f"connecting to boundary, side {side}")
        with ExitStack() as stack:
            yield self.create_connection(**{
                name: stack.enter_context(self.open_pipe(name, side))
                for name in self.pipe_info
            })
