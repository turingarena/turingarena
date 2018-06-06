from abc import abstractmethod, ABCMeta
from collections import namedtuple
from typing import List, Optional

from turingarena_impl.interface.variables import ReferenceDirection, ReferenceAction

AbstractSyntaxNodeWrapper = namedtuple("AbstractSyntaxNodeWrapper", ["ast", "context"])


class IntermediateNode:
    __slots__ = []

    @property
    def reference_actions(self) -> List[ReferenceAction]:
        """
        List of references involved in this instruction.
        """
        actions = list(self._get_reference_actions())
        assert all(isinstance(a, ReferenceAction) for a in actions)
        return actions

    @property
    def direction(self) -> Optional[ReferenceDirection]:
        return self._get_direction()

    @abstractmethod
    def _get_reference_actions(self):
        pass

    @abstractmethod
    def _get_direction(self):
        pass

    def on_execute(self, bindings, runner):
        pass

    def on_request_lookahead(self, bindings, request):
        pass

    def on_generate_response(self, bindings):
        pass

    def on_communicate_upward(self, bindings, lines):
        pass

    def on_communicate_downward(self, bindings, lines):
        pass


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


class Step(IntermediateNode, namedtuple("Step", ["children"])):
    __slots__ = []

    def __init__(self, *args, **kwargs):
        super().__init__()
        assert self.children

        if self.direction is None:
            assert len(self.children) == 1
        else:
            assert all(n.direction is self.direction for n in self.children)

    def _get_direction(self):
        return self.children[0].direction

    def _get_reference_actions(self):
        for n in self.children:
            yield from n.reference_actions


class StatementIntermediateNode(IntermediateNode, namedtuple("StatementIntermediateNode", ["statement"])):
    __slots__ = []
