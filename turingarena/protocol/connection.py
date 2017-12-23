from turingarena.common import ImmutableObject


class ProxyConnection(ImmutableObject):
    __slots__ = ["request_pipe", "response_pipe", "error_pipe"]
