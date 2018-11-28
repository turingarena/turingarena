import logging
from collections import namedtuple

from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.control import ControlStructure
from turingarena.driver.interface.statements.statement import Statement

logger = logging.getLogger(__name__)


class SwitchNode(namedtuple("SwitchNode", ["value", "cases"]), IntermediateNode):
    __slots__ = []


class Switch(ControlStructure, SwitchNode):
    __slots__ = []

    def _get_bodies(self):
        for c in self.cases:
            yield c.body

    def _describe_node(self):
        yield f"switch {self.value} "
        for c in self.cases:
            yield from self._indent_all(self._describe_case(c))

    def _describe_case(self, case):
        labels = ", ".join(str(l.value) for l in case.labels)
        yield f"case {labels}"
        yield from self._indent_all(case.body.node_description)


class Case(namedtuple("Case", ["labels", "body"])):
    __slots__ = []


class SwitchValueResolve(SwitchNode):
    def _describe_node(self):
        yield f"resolve {self}"
