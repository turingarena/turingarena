import logging
from collections import namedtuple

from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.control import ControlStructure

logger = logging.getLogger(__name__)


class SwitchNode(namedtuple("SwitchNode", ["value", "cases"]), IntermediateNode):
    __slots__ = []


class Switch(ControlStructure, SwitchNode):
    __slots__ = []

    def _get_bodies(self):
        for c in self.cases:
            yield c.body

class Case(namedtuple("Case", ["labels", "body"])):
    __slots__ = []


class SwitchValueResolve(SwitchNode):
    def _describe_node(self):
        yield f"resolve {self}"
