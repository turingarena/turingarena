import logging
from collections import namedtuple

from turingarena_impl.interface.common import ImperativeStructure, AbstractSyntaxNodeWrapper, memoize
from turingarena_impl.interface.diagnostics import Diagnostic
from turingarena_impl.interface.expressions import SyntheticExpression
from turingarena_impl.interface.nodes import IntermediateNode
from turingarena_impl.interface.statements.statement import Statement, SyntheticStatement
from turingarena_impl.interface.step import Step

logger = logging.getLogger(__name__)


class Block(ImperativeStructure, AbstractSyntaxNodeWrapper):
    __slots__ = []

    def _generate_statements(self):
        inner_context = self.context
        for s in self.ast.statements:
            statement = Statement.compile(s, inner_context)

            for inst in statement.intermediate_nodes:
                inner_context = inner_context.with_reference_actions(inst.reference_actions)

            yield statement

    @property
    @memoize
    def statements(self):
        return list(self._generate_statements())

    def validate(self):
        from turingarena_impl.interface.statements.loop import BreakStatement
        from turingarena_impl.interface.statements.callback import ExitStatement

        for i, statement in enumerate(self.statements):
            yield from statement.validate()
            if isinstance(statement, BreakStatement) or isinstance(statement, ExitStatement):
                if i < len(self.statements) - 1:
                    yield Diagnostic(Diagnostic.Messages.UNREACHABLE_CODE, parseinfo=self.ast.parseinfo)
                    break

    @property
    @memoize
    def synthetic_statements(self):
        for s in self.statements:
            yield s
            if s.statement_type == "call" and s.method.has_callbacks:
                yield SyntheticStatement("write", arguments=[
                    SyntheticExpression("int_literal", value=0),  # no more callbacks
                ])

    @property
    @memoize
    def flat_inner_nodes(self):
        return list(self._generate_flat_inner_nodes())

    def _generate_flat_inner_nodes(self):
        for s in self.statements:
            yield from s.intermediate_nodes

    def expects_request(self, request):
        for s in self.statements:
            if s.expects_request(request):
                return True
            if not s.expects_request(None):
                break


class BlockNode(IntermediateNode, namedtuple("BlockNode", ["children"])):
    @staticmethod
    def _group_nodes_by_direction(nodes):
        group = []
        for node in nodes:
            if node.can_be_grouped and len(BlockNode.group_directions(group + [node])) <= 1:
                group.append(node)
                continue

            if group:
                yield Step(tuple(group))
                group.clear()

            if not node.can_be_grouped:
                yield node
            else:
                group.append(node)

        if group:
            yield Step(tuple(group))

    @staticmethod
    def group_directions(group):
        return {d for n in group for d in n.declaration_directions}

    @staticmethod
    def from_nodes(nodes):
        return BlockNode(tuple(BlockNode._group_nodes_by_direction(nodes)))

    def _driver_run(self, context):
        assignments = []
        for n in self.children:
            inner_assigments = n.driver_run(context)
            assignments.extend(inner_assigments)
            context = context.with_assigments(inner_assigments)
        return assignments

    def _get_reference_actions(self):
        for n in self.children:
            yield from n.reference_actions

    def _get_declaration_directions(self):
        for n in self.children:
            yield from n.declaration_directions
