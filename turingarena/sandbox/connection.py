from turingarena.common import ImmutableObject


class ProcessConnection(ImmutableObject):
    __slots__ = ["downward_pipe", "upward_pipe", "error_pipe"]
