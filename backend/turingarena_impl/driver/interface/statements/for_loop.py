import logging
from collections import namedtuple

from turingarena_impl.driver.interface.block import Block, BlockNode
from turingarena_impl.driver.interface.expressions import Expression
from turingarena_impl.driver.interface.nodes import IntermediateNode
from turingarena_impl.driver.interface.phase import ExecutionPhase
from turingarena_impl.driver.interface.statements.statement import Statement
from turingarena_impl.driver.interface.variables import Variable, Allocation, ReferenceStatus, ReferenceAction

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

    def _get_first_requests(self):
        yield None
        yield from self.body.first_requests

    def validate(self):
        yield from self.body.validate()

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
        needed = not self.can_be_grouped or context.phase is ExecutionPhase.REQUEST or any(
            a.status.name() == context.phase.name()  # FIXME: using name()
            for a in self.reference_actions
        )
        if not needed:
            logger.debug(f"skipping for (phase: {context.phase})")
            return

        if context.phase is None:
            assert context.request_lookahead is None

        for_range = self.index.range.evaluate(context.bindings)

        results_by_iteration = [
            self._body_node.driver_run(context.with_assigments(
                [(self.index.variable.as_reference(), i)]
            ))
            for i in range(for_range)
        ]

        assignments = [
            (a.reference, [
                result.assignments[a.reference._replace(
                    index_count=a.reference.index_count + 1,
                )]
                for result in results_by_iteration
                if a.status is ReferenceStatus.RESOLVED
            ])
            for a in self.reference_actions
        ]

        return context.result()._replace(assignments=assignments)

    def _describe_node(self):
        yield f"for {self.index.variable.name} to {self.index.range}"
        yield from self._indent_all(self._body_node.node_description)
