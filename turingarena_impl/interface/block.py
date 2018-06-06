import logging
from itertools import groupby
from typing import List

from turingarena_impl.interface.common import ImperativeStructure, AbstractSyntaxNodeWrapper
from turingarena_impl.interface.diagnostics import Diagnostic
from turingarena_impl.interface.expressions import SyntheticExpression
from turingarena_impl.interface.nodes import Bindings
from turingarena_impl.interface.statements.statement import Statement, SyntheticStatement
from turingarena_impl.interface.step import Step, RunnableNode, StepExecutor
from turingarena_impl.interface.variables import ReferenceDirection

logger = logging.getLogger(__name__)


class Block(ImperativeStructure, RunnableNode, AbstractSyntaxNodeWrapper):
    __slots__ = []

    def _generate_statements(self):
        inner_context = self.context
        for s in self.ast.statements:
            statement = Statement.compile(s, inner_context)

            for inst in statement.intermediate_nodes:
                inner_context = inner_context.with_reference_actions(inst.reference_actions)

            yield statement

    @property
    def statements(self):
        return list(self._generate_statements())

    def validate(self):
        from turingarena_impl.interface.statements.loop import BreakStatement
        from turingarena_impl.interface.statements.exit import ExitStatement

        for i, statement in enumerate(self.statements):
            yield from statement.validate()
            if isinstance(statement, BreakStatement) or isinstance(statement, ExitStatement):
                if i < len(self.statements) - 1:
                    yield Diagnostic(Diagnostic.Messages.UNREACHABLE_CODE, parseinfo=self.ast.parseinfo)
                    break

    @property
    def synthetic_statements(self):
        for s in self.statements:
            yield s
            if s.statement_type == "call" and s.method.has_callbacks:
                yield SyntheticStatement("write", arguments=[
                    SyntheticExpression("int_literal", value=0),  # no more callbacks
                ])

    def _generate_flat_inner_nodes(self):
        for s in self.statements:
            yield from s.intermediate_nodes

    def _group_nodes_by_direction(self):
        for k, g in groupby(self._generate_flat_inner_nodes(), key=lambda inst: inst.direction):
            if k is None:
                yield from g
            else:
                assert isinstance(k, ReferenceDirection)
                yield Step(list(g))

    @property
    def children(self) -> List[RunnableNode]:
        return list(self._group_nodes_by_direction())

    def _get_reference_actions(self):
        for n in self.children:
            yield from n.reference_actions

    def _get_direction(self):
        if len(self.children) == 1:
            return self.children[0].direction
        else:
            return None

    def expects_request(self, request):
        for s in self.statements:
            if s.expects_request(request):
                return True
            if not s.expects_request(None):
                break

    @property
    def may_process_requests(self):
        return any(
            s.may_process_requests
            for s in self.statements
        )

    def driver_run(self, bindings: Bindings, executor: StepExecutor):
        assignments = []
        for n in self.children:
            assignments.extend(n.driver_run({
                **bindings,
                **dict(assignments),
            }, executor))
        return assignments
