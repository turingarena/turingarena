from collections import namedtuple
from typing import Mapping, Any

from turingarena.driver.interface.variables import Reference

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

    @property
    def node_description(self):
        return list(self._describe_node())

    @staticmethod
    def _indent_all(lines):
        for l in lines:
            yield "  " + l

    def _describe_node(self):
        yield str(self)
