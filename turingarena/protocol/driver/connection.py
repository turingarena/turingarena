from turingarena.common import ImmutableObject


class DriverProcessConnection(ImmutableObject):
    __slots__ = ["request", "response"]
