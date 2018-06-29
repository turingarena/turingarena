import logging
from collections import namedtuple
from typing import List, Mapping, Any

from turingarena_impl.driver.interface.variables import ReferenceAction, Reference, ReferenceStatus

Bindings = Mapping[Reference, Any]


class ExecutionResult(namedtuple("ExecutionResult", [
    "assignments",
    "request_lookahead",
    "does_break",
])):
    def merge(self, other):
        return ExecutionResult(
            self.assignments + other.assignments,
            request_lookahead=other.request_lookahead,
            does_break=other.does_break,
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

    def driver_run(self, context):
        logging.debug(f"driver_run: {type(self).__name__} phase: {context.phase}")

        result = self._driver_run(context)
        if result is None:
            result = context.result()
        return result

    def _driver_run(self, context):
        return None

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
        if not context.is_first_execution:
            return
        if context.request_lookahead is not None:
            return
        return context.result()._replace(
            request_lookahead=context.next_request(),
        )

    def _describe_node(self):
        yield "next request"
