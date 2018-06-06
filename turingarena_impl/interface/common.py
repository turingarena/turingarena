from abc import abstractmethod, ABCMeta
from collections import namedtuple
from typing import List

from turingarena_impl.interface.nodes import IntermediateNode

AbstractSyntaxNodeWrapper = namedtuple("AbstractSyntaxNodeWrapper", ["ast", "context"])


class ImperativeStructure(metaclass=ABCMeta):
    __slots__ = []

    @abstractmethod
    def expects_request(self, request):
        pass

    @property
    def may_process_requests(self):
        return False

    @property
    def intermediate_nodes(self) -> List[IntermediateNode]:
        return list(self._get_intermediate_nodes())

    @abstractmethod
    def _get_intermediate_nodes(self):
        pass
