import logging

from turingarena.common import ImmutableObject
from turingarena.pipeboundary import PipeBoundary

logger = logging.getLogger(__name__)


class SandboxConnection(ImmutableObject):
    __slots__ = ["downward", "upward"]


class SandboxBoundary(PipeBoundary):
    __slots__ = []

    pipe_info = {
        "downward": ("w", "r"),
        "upward": ("r", "w"),
    }
    create_connection = SandboxConnection
