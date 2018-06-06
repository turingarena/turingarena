from abc import abstractmethod
from collections import namedtuple
from typing import List, Optional, Mapping, Any

from turingarena_impl.interface.variables import ReferenceAction, ReferenceDirection, Reference

Bindings = Mapping[Reference, Any]


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


class StatementIntermediateNode(IntermediateNode, namedtuple("StatementIntermediateNode", ["statement"])):
    __slots__ = []
