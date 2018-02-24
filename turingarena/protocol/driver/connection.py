from turingarena.common import ImmutableObject
from turingarena.pipeboundary import PipeBoundary


class DriverProcessConnection(ImmutableObject):
    __slots__ = ["request", "response"]


class DriverProcessBoundary(PipeBoundary):
    __slots__ = []

    def pipe_info(self):
        return {
            "request": ("w", "r"),
            "response": ("r", "w"),
        }
