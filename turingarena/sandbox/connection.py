import logging

from turingarena.common import ImmutableObject
from turingarena.pipeboundary import PipeBoundary

logger = logging.getLogger(__name__)


class SandboxConnection(ImmutableObject):
    __slots__ = ["request", "response"]


class SandboxBoundary(PipeBoundary):
    __slots__ = []

    pipe_info = {
        "request": ("w", "r"),
        "response": ("r", "w"),
    }


class SandboxProcessConnection(ImmutableObject):
    __slots__ = ["downward", "upward"]


class SandboxProcessBoundary(PipeBoundary):
    __slots__ = []

    pipe_info = {
        "downward": ("w", "r"),
        "upward": ("r", "w"),
    }


class SandboxProcessWaitBarrier(PipeBoundary):
    __slots__ = []
    pipe_info = {
        "wait_barrier": ("w", "r"),
    }
