import logging
from collections import namedtuple

from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.control import ControlStructure

logger = logging.getLogger(__name__)

ForIndex = namedtuple("ForIndex", ["variable", "range"])


class For(namedtuple("For", ["index", "body"]), ControlStructure, IntermediateNode):
    __slots__ = []

    def _get_bodies(self):
        yield self.body

    def _describe_node(self):
        yield f"for {self.index.variable.name} to {self.index.range}"
        yield from self._indent_all(self.body.node_description)
