from turingarena.common import ImmutableObject


class DriverConnection(ImmutableObject):
    __slots__ = ["request_pipe", "response_pipe"]
