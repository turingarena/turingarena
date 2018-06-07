import logging
from abc import abstractmethod
from collections import namedtuple
from typing import List, Optional, Mapping, Any

from turingarena_impl.interface.engine import NodeExecutionContext
from turingarena_impl.interface.instructions import Assignments
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

    def driver_run(self, context: NodeExecutionContext) -> Assignments:
        logging.debug(f"driver_run: {type(self).__name__} phase: {context.phase}")

        assignments = self._driver_run(context)
        if assignments is None:
            assignments = []
        else:
            assignments = list(assignments)
        assert all(isinstance(r, Reference) for r, v in assignments)
        return assignments

    @abstractmethod
    def _driver_run(self, context):
        pass

    def _run_node_sequence(self, nodes, context: NodeExecutionContext):
        assignments = []
        for n in nodes:
            assignments.extend(n.driver_run(context.with_assigments(assignments)))
        return assignments


class StatementIntermediateNode(IntermediateNode, namedtuple("StatementIntermediateNode", ["statement"])):
    __slots__ = []
