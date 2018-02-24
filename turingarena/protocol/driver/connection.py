from turingarena.common import ImmutableObject
from turingarena.pipeboundary import PipeBoundary


class DriverProcessConnection(ImmutableObject):
    __slots__ = ["request", "response"]


class DriverProcessBoundary(PipeBoundary):
    __slots__ = []

    pipe_info = {
        "request": ("w", "r"),
        "response": ("r", "w"),
    }
    create_connection = DriverProcessConnection
