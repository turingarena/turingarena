import logging
from collections import namedtuple

from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.control import ControlStructure

logger = logging.getLogger(__name__)


class IfNode(namedtuple("IfNode", ["condition", "then_body", "else_body"]), IntermediateNode):
    __slots__ = []

    @property
    def branches(self):
        return tuple(
            b
            for b in (self.then_body, self.else_body)
            if b is not None
        )


class If(ControlStructure, IfNode):
    def _get_bodies(self):
        yield self.then_body
        if self.else_body is not None:
            yield self.else_body

    def _describe_node(self):
        yield f"if {self.condition}"
        yield from self._indent_all(self.then_body.node_description)
        if self.else_body is not None:
            yield "else"
            yield from self._indent_all(self.else_body.node_description)


class IfConditionResolve(IfNode):
    def _describe_node(self):
        yield "resolve if"
