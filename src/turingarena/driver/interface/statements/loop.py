import logging

from turingarena.driver.interface.block import Block
from turingarena.driver.interface.diagnostics import Diagnostic
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.control import ControlStructure
from turingarena.driver.interface.statements.statement import Statement

logger = logging.getLogger(__name__)


class Loop(Statement, ControlStructure, IntermediateNode):
    __slots__ = []

    def _get_bodies(self):
        yield self.body

    @property
    def body(self):
        return Block(ast=self.ast.body, context=self.context.with_loop())

    def _describe_node(self):
        yield "loop"
        yield from self._indent_all(self.body.node_description)


class Break(Statement, IntermediateNode):
    __slots__ = []
