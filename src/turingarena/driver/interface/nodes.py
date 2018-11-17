import logging
from collections import namedtuple
from typing import List, Mapping, Any

from turingarena.driver.interface.phase import ExecutionPhase
from turingarena.driver.interface.variables import ReferenceAction, Reference, ReferenceStatus

Bindings = Mapping[Reference, Any]


class ExecutionResult(namedtuple("ExecutionResult", [
    "assignments",
    "request_lookahead",
    "does_break",
])):
    def merge(self, other):
        if other is None:
            return self

        return ExecutionResult(
            self.assignments + other.assignments,
            request_lookahead=other.request_lookahead,
            does_break=other.does_break,
        )

    def with_request_processed(self):
        return self._replace(request_lookahead=None)


class IntermediateNode:
    __slots__ = []

    def validate(self):
        return []

    @property
    def needs_flush(self):
        return False

    @property
    def variables_to_declare(self):
        return frozenset(self._get_variables_to_declare())

    def _should_declare_variables(self):
        return False

    def _get_variables_to_declare(self):
        if not self._should_declare_variables():
            return
        for a in self.reference_actions:
            if a.reference.index_count == 0 and a.status == ReferenceStatus.DECLARED:
                yield a.reference.variable

    @property
    def allocations(self):
        return list(self._get_allocations())

    def _get_allocations(self):
        return []

    @property
    def comment(self):
        return self._get_comment()

    def _get_comment(self):
        return None

    @property
    def does_break(self):
        return False

    @property
    def is_relevant(self):
        "Whether this node should be kept in the parent block"
        return self._is_relevant()

    def _is_relevant(self):
        return True

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

    @property
    def first_requests(self):
        return frozenset(self._get_first_requests())

    def _get_first_requests(self):
        yield None

    def driver_run(self, context):
        should_lookahead_request = (
                context.request_lookahead is None
                and self.needs_request_lookahead
                and context.phase is ExecutionPhase.REQUEST
        )

        result = context.result()
        if should_lookahead_request:
            lookahead = context.next_request()
            result = result._replace(
                request_lookahead=lookahead,
            )
            context = context.extend(result)

        logging.debug(
            f"driver_run: {type(self).__name__} "
            f"phase: {context.phase} "
            f"request LA: {context.request_lookahead}"
        )

        return result.merge(self._driver_run(context))

    def _driver_run(self, context):
        return None

    @property
    def can_be_grouped(self):
        return self._can_be_grouped()

    def _can_be_grouped(self):
        return True

    @property
    def needs_request_lookahead(self):
        return self._needs_request_lookahead()

    def _needs_request_lookahead(self):
        return False

    @property
    def node_description(self):
        return list(self._describe_node())

    @staticmethod
    def _indent_all(lines):
        for l in lines:
            yield "  " + l

    def _describe_node(self):
        yield str(self)
