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
    __slots__ = []

    def _get_bodies(self):
        yield self.then_body
        if self.else_body is not None:
            yield self.else_body


class IfConditionResolve(IfNode):
    __slots__ = []

