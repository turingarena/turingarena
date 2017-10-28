class ImmutableObject:
    __slots__ = []

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class AbstractSyntaxNode(ImmutableObject):
    __slots__ = []
