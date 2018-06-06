from abc import abstractmethod
from collections import namedtuple
from typing import List, Optional

from turingarena_impl.interface.variables import ReferenceAction, ReferenceDirection


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


class StatementIntermediateNode(IntermediateNode, namedtuple("StatementIntermediateNode", ["statement"])):
    __slots__ = []
