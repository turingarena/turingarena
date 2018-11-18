import logging
from collections import namedtuple

from turingarena.driver.interface.block import Block
from turingarena.driver.interface.expressions import Expression
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.statement import Statement
from turingarena.driver.interface.variables import Variable, VariableAllocation, ReferenceStatus, ReferenceAction

logger = logging.getLogger(__name__)

ForIndex = namedtuple("ForIndex", ["variable", "range"])


class For(Statement, IntermediateNode):
    __slots__ = []

    @property
    def index(self):
        index_context = self.context.expression()
        return ForIndex(
            variable=Variable(name=self.ast.index, dimensions=0),
            range=Expression.compile(self.ast.range, index_context),
        )

    @property
    def body(self):
        return Block(
            ast=self.ast.body,
            context=self.context.with_index_variable(self.index).with_reference_actions([
                ReferenceAction(self.index.variable.as_reference(), ReferenceStatus.DECLARED),
                ReferenceAction(self.index.variable.as_reference(), ReferenceStatus.RESOLVED),
            ]),
        )

    def _get_allocations(self):
        for a in self.body.reference_actions:
            if a.reference.variable.dimensions == 0:
                continue
            if a.status == ReferenceStatus.DECLARED:
                yield VariableAllocation(
                    variable=a.reference.variable,
                    indexes=self.context.index_variables[-a.reference.index_count + 1:],
                    size=self.index.range,
                )

    def _get_intermediate_nodes(self):
        yield self

    def _should_declare_variables(self):
        return True

    def validate(self):
        yield from self.index.range.validate()
        yield from self.body.validate()

    def _get_declaration_directions(self):
        return self.body.declaration_directions

    def _get_reference_actions(self):
        for a in self.body.reference_actions:
            r = a.reference
            if r.index_count > 0:
                yield a._replace(reference=r._replace(index_count=r.index_count - 1))

    def _can_be_grouped(self):
        # no local references
        r = all(
            a.reference.index_count > 0
            for a in self.body.reference_actions
        ) and all(
            child.can_be_grouped
            for child in self.body.children
        )
        return r

    def _describe_node(self):
        yield f"for {self.index.variable.name} to {self.index.range}"
        yield from self._indent_all(self.body.node_description)
