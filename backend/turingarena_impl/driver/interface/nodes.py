import logging
from abc import abstractmethod
from collections import namedtuple
from typing import List, Mapping, Any

from turingarena_impl.driver.interface.execution import NodeExecutionContext, Assignments
from turingarena_impl.driver.interface.variables import ReferenceAction, Reference

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

    def _get_reference_actions(self):
        return []

    @property
    def declaration_directions(self):
        return frozenset(self._get_declaration_directions())

    def _get_declaration_directions(self):
        return frozenset()

    def driver_run(self, context: NodeExecutionContext) -> Assignments:
        logging.debug(f"driver_run: {type(self).__name__} phase: {context.phase}")

        assignments = self._driver_run(context)
        if assignments is None:
            assignments = []
        else:
            assignments = list(assignments)
        assert all(isinstance(r, Reference) for r, v in assignments)
        return assignments

    @property
    def can_be_grouped(self):
        return self._can_be_grouped() and len(self.declaration_directions) <= 1

    def _can_be_grouped(self):
        return True

    @abstractmethod
    def _driver_run(self, context):
        pass


class StatementIntermediateNode(IntermediateNode, namedtuple("StatementIntermediateNode", ["statement"])):
    __slots__ = []
