import logging
from collections import namedtuple

from turingarena_impl.interface.block import Block
from turingarena_impl.interface.engine import NodeExecutionContext
from turingarena_impl.interface.expressions import Expression
from turingarena_impl.interface.nodes import IntermediateNode
from turingarena_impl.interface.statements.statement import Statement
from turingarena_impl.interface.variables import Variable, Allocation, ReferenceStatus, Reference

logger = logging.getLogger(__name__)

ForIndex = namedtuple("ForIndex", ["variable", "range"])


class ForStatement(Statement, IntermediateNode):
    __slots__ = []

    @property
    def index(self):
        return ForIndex(
            variable=Variable(name=self.ast.index, dimensions=0),
            range=Expression.compile(self.ast.range, self.context),
        )

    @property
    def body(self):
        return Block(
            ast=self.ast.body,
            context=self.context.with_index_variable(self.index),
        )

    def _get_allocations(self):
        for a in self.body.reference_actions:
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

    @property
    def may_process_requests(self):
        return self.body.may_process_requests

    def expects_request(self, request):
        return (
            request is None
            or self.body.expects_request(request)
        )

    def _get_direction(self):
        return self.body.direction

    def _get_reference_actions(self):
        for a in self.body.reference_actions:
            r = a.reference
            if r.index_count > 0:
                yield a._replace(reference=r._replace(index_count=r.index_count - 1))

    def _driver_run(self, context):
        assignments_by_iteration = [
            self.body.driver_run(context.with_assigments(
                [(Reference(variable=self.index.variable, index_count=0), i)]
            ))
            for i in range(self.index.range.evaluate(context.bindings))
        ]
        return {
            a.reference: [
                assignments[a.reference._replace(
                    index_count=a.reference.index_count + 1,
                )]
                for assignments in assignments_by_iteration
            ]
            for a in self.reference_actions
            if a.status is ReferenceStatus.RESOLVED
        }
