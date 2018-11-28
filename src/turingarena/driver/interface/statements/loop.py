import logging
from collections import namedtuple

from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.control import ControlStructure

logger = logging.getLogger(__name__)


class Loop(namedtuple("Loop", ["body"]), ControlStructure, IntermediateNode):
    __slots__ = []

    def _get_bodies(self):
        yield self.body

    def _describe_node(self):
        yield "loop"
        yield from self._indent_all(self.body.node_description)


class Break(namedtuple("Break", []), IntermediateNode):
    __slots__ = []
