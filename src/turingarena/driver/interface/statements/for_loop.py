import logging
from collections import namedtuple

from turingarena.driver.interface.block import Block
from turingarena.driver.interface.expressions import Expression
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.control import ControlStructure
from turingarena.driver.interface.statements.statement import Statement
from turingarena.driver.interface.variables import Variable, ReferenceDeclaration, ReferenceResolution

logger = logging.getLogger(__name__)

ForIndex = namedtuple("ForIndex", ["variable", "range"])


class For(Statement, ControlStructure, IntermediateNode):
    __slots__ = []

    @property
    def index(self):
        index_context = self.context.expression()
        return ForIndex(
            variable=Variable(name=self.ast.index, dimensions=0),
            range=Expression.compile(self.ast.range, index_context),
        )

    def _get_bodies(self):
        yield self.body

    @property
    def body(self):
        return Block(
            ast=self.ast.body,
            context=self.context.with_index_variable(self.index).with_reference_actions([
                ReferenceDeclaration(self.index.variable.as_reference(), dimensions=0),
                ReferenceResolution(self.index.variable.as_reference()),
            ]),
        )

    def _get_intermediate_nodes(self):
        yield self

    def _describe_node(self):
        yield f"for {self.index.variable.name} to {self.index.range}"
        yield from self._indent_all(self.body.node_description)
