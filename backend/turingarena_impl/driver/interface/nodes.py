import logging
from collections import namedtuple
from typing import List, Mapping, Any

from turingarena_impl.driver.interface.execution import NodeExecutionContext
from turingarena_impl.driver.interface.variables import ReferenceAction, Reference, ReferenceStatus, ReferenceDirection

Bindings = Mapping[Reference, Any]


class ExecutionResult(namedtuple("ExecutionResult", ["assignments", "request_lookahead"])):
    def merge(self, other):
        request_lookahead = other.request_lookahead
        if request_lookahead is None:
            request_lookahead = self.request_lookahead
        return ExecutionResult(
            self.assignments + other.assignments,
            request_lookahead=request_lookahead,
        )


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

    def driver_run(self, context: NodeExecutionContext) -> ExecutionResult:
        logging.debug(f"driver_run: {type(self).__name__} phase: {context.phase}")

        assignments = self._driver_run_assignments(context)
        simple = self._driver_run_simple(context)
        full = self._driver_run(context)

        assert (assignments, simple, full).count(NotImplemented) == 2

        if assignments is not NotImplemented:
            return ExecutionResult(list(assignments), None)

        if simple is not NotImplemented:
            return ExecutionResult([], None)

        if full is not NotImplemented:
            assert isinstance(full, ExecutionResult)
            return full

        return assignments

    def _driver_run_simple(self, context):
        return NotImplemented

    def _driver_run_assignments(self, context):
        return NotImplemented

    def _driver_run(self, context):
        return NotImplemented

    @property
    def can_be_grouped(self):
        return self._can_be_grouped() and len(self.declaration_directions) <= 1

    def _can_be_grouped(self):
        return True

    @property
    def node_description(self):
        return list(self._describe_node())

    def _indent_all(self, lines):
        for l in lines:
            yield "  " + l

    def _describe_node(self):
        yield str(self)


class StatementIntermediateNode(IntermediateNode, namedtuple("StatementIntermediateNode", ["statement"])):
    __slots__ = []


class RequestLookaheadNode(IntermediateNode):
    def _driver_run(self, context):
        # FIXME: copied from CallStatement
        should_run = (
                context.direction is ReferenceDirection.UPWARD
                and context.phase is ReferenceStatus.DECLARED
                or context.direction is not ReferenceDirection.UPWARD
                and context.phase is ReferenceStatus.RESOLVED
        )
        if not should_run:
            return ExecutionResult([], None)
        return ExecutionResult([], context.next_request())

    def _describe_node(self):
        yield "next request"
