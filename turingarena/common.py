from abc import ABCMeta


class ImmutableObject(metaclass=ABCMeta):
    __slots__ = []

    def __init__(self, **kwargs):
        assert len(kwargs) == len(list(self.all_slots()))
        for k, v in kwargs.items():
            object.__setattr__(self, k, v)

    @classmethod
    def all_slots(cls):
        for base in cls.mro():
            if base == object: continue
            yield from base.__slots__

    def __repr__(self):
        args = ", ".join(f"{s}={repr(getattr(self, s, '<MISSING>'))}" for s in self.all_slots())
        return f"{self.__class__.__name__}({args})"


class TupleLikeObject(ImmutableObject):
    __slots__ = []

    def _to_tuple(self):
        return tuple(getattr(self, s) for s in self.__slots__)

    def __eq__(self, other):
        return (
            isinstance(other, TupleLikeObject)
            and self._to_tuple() == other._to_tuple()
        )

    def __hash__(self):
        return hash(self._to_tuple())


def indent_all(lines):
    for line in lines:
        yield indent(line)


def indent(line):
    if line is None:
        return None
    else:
        return "    " + line


def write_to_file(lines, file):
    for line in lines:
        if line is None:
            print("", file=file)
        else:
            print(line, file=file)
