import logging
from collections import namedtuple

from turingarena_impl.interface.block import Block, BlockNode
from turingarena_impl.interface.context import ExpressionContext
from turingarena_impl.interface.expressions import Expression
from turingarena_impl.interface.nodes import IntermediateNode
from turingarena_impl.interface.statements.statement import Statement
from turingarena_impl.interface.variables import Variable, Allocation, ReferenceStatus, Reference, ReferenceAction

logger = logging.getLogger(__name__)

ForIndex = namedtuple("ForIndex", ["variable", "range"])


class ForStatement(Statement, IntermediateNode):
    __slots__ = []

    @property
    def index(self):
        index_context = self.context.expression(declaring=True)
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
        for a in self._body_node.reference_actions:
            if a.reference.variable.dimensions == 0:
                continue
            if a.status == ReferenceStatus.DECLARED:
                yield Allocation(
                    reference=a.reference._replace(
                        index_count=a.reference.index_count - 1,
                    ),
                    size=self.index.range,
                )

    def _get_intermediate_nodes(self):
        yield self

    def validate(self):
        yield from self.body.validate()

    def expects_request(self, request):
        return (
            request is None
            or self.body.expects_request(request)
        )

    def _get_declaration_directions(self):
        return self._body_node.declaration_directions

    def _get_reference_actions(self):
        for a in self._body_node.reference_actions:
            r = a.reference
            if r.index_count > 0:
                yield a._replace(reference=r._replace(index_count=r.index_count - 1))

    def _can_be_grouped(self):
        # no local references
        return all(
            a.reference.index_count > 0
            for a in self._body_node.reference_actions
        )

    @property
    def _body_node(self):
        return BlockNode.from_nodes(self.body.flat_inner_nodes)

    def _driver_run(self, context):
        needed = not self.can_be_grouped or any(
            a.status is context.phase
            for a in self.reference_actions
        )
        if not needed:
            logger.debug(f"skipping for (phase: {context.phase})")
            return

        for_range = self.index.range.evaluate(context.bindings)

        assignments_by_iteration = [
            self._body_node.driver_run(context.with_assigments(
                [(Reference(variable=self.index.variable, index_count=0), i)]
            ))
            for i in range(for_range)
        ]

        for a in self.reference_actions:
            if a.status is ReferenceStatus.RESOLVED:
                yield a.reference, [
                    assignments[a.reference._replace(
                        index_count=a.reference.index_count + 1,
                    )]
                    for assignments in assignments_by_iteration
                ]
