import logging

from turingarena.driver.interface.block import Block
from turingarena.driver.interface.diagnostics import Diagnostic
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.statement import Statement

logger = logging.getLogger(__name__)


class Loop(Statement, IntermediateNode):
    __slots__ = []

    def _get_declaration_directions(self):
        return self.body.declaration_directions

    def _get_reference_actions(self):
        return []

    def _can_be_grouped(self):
        return False

    @property
    def body(self):
        return Block(ast=self.ast.body, context=self.context.with_loop())

    def validate(self):
        yield from self.body.validate()

    def _describe_node(self):
        yield "loop"
        yield from self._indent_all(self.body.node_description)


class Break(Statement, IntermediateNode):
    __slots__ = []

    def _get_reference_actions(self):
        return []

    def validate(self):
        if not self.context.in_loop:
            yield Diagnostic(Diagnostic.Messages.UNEXPECTED_BREAK, parseinfo=self.ast.parseinfo)
