from abc import abstractmethod, ABCMeta
from collections import namedtuple
from functools import lru_cache

memoize = lru_cache(None, typed=True)


class AbstractSyntaxNodeWrapper(namedtuple("AbstractSyntaxNodeWrapper", ["ast", "context"])):
    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        return self is other


class ImperativeStructure(metaclass=ABCMeta):
    __slots__ = []

    @abstractmethod
    def expects_request(self, request):
        pass
