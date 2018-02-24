import logging

from turingarena.common import ImmutableObject
from turingarena.pipeboundary import PipeBoundary

logger = logging.getLogger(__name__)


class SandboxProcessConnection(ImmutableObject):
    __slots__ = ["downward", "upward"]


class SandboxProcessBoundary(PipeBoundary):
    __slots__ = []

    pipe_info = {
        "downward": ("w", "r"),
        "upward": ("r", "w"),
    }
    create_connection = SandboxProcessConnection


class SandboxProcessWaitBarrier(PipeBoundary):
    __slots__ = []
    pipe_info = {
        "wait_barrier": ("w", "r"),
    }

    def create_connection(self, wait_barrier):
        return None
