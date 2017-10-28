class ImmutableObject:
    __slots__ = []

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def _to_tuple(self):
        return tuple(getattr(self, s) for s in self.__slots__)

    def __eq__(self, other):
        return (
            isinstance(other, ImmutableObject)
            and self._to_tuple() == other._to_tuple()
        )

    def __hash__(self):
        return hash(self._to_tuple())


class AbstractSyntaxNode(ImmutableObject):
    __slots__ = []
