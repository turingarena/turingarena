import logging
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

    @property
    def has_request_lookahead(self):
        has_request_lookahead = self._get_has_request_lookahead()
        assert isinstance(has_request_lookahead, bool)
        return has_request_lookahead

    @abstractmethod
    def _get_has_request_lookahead(self):
        pass

    @abstractmethod
    def expects_request(self, request):
        pass
