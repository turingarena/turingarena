import logging
from collections import namedtuple

from turingarena_impl.driver.interface.common import ImperativeStructure, AbstractSyntaxNodeWrapper, memoize
from turingarena_impl.driver.interface.diagnostics import Diagnostic
from turingarena_impl.driver.interface.expressions import SyntheticExpression
from turingarena_impl.driver.interface.nodes import IntermediateNode, ExecutionResult
from turingarena_impl.driver.interface.statements.statement import Statement, SyntheticStatement
from turingarena_impl.driver.interface.step import Step

logger = logging.getLogger(__name__)


class Block(ImperativeStructure, AbstractSyntaxNodeWrapper):
    __slots__ = []

    def _generate_statements(self):
        inner_context = self.context._replace(main_block=False)
        for s in self.ast.statements:
            statement = Statement.compile(s, inner_context)

            for inst in statement.intermediate_nodes:
                inner_context = inner_context.with_reference_actions(inst.reference_actions)

            yield statement

    @property
    @memoize
    def statements(self):
        return tuple(self._generate_statements())

    def validate(self):
        exited = False
        for statement in self.statements:
            if exited:
                yield Diagnostic(Diagnostic.Messages.UNREACHABLE_CODE, parseinfo=self.ast.parseinfo)
                break
            yield from statement.validate()
            if statement.does_break:
                exited = True

    @property
    @memoize
    def synthetic_statements(self):
        return tuple(self._generate_synthetic_statements())

    def _generate_synthetic_statements(self):
        if self.context.main_block:
            yield SyntheticStatement("checkpoint", "ready", arguments=[])

        for s in self.statements:
            yield s
            if s.statement_type == "call" and s.method.has_callbacks:
                yield SyntheticStatement("write", "no more callbacks", arguments=[
                    SyntheticExpression("int_literal", value=0),
                ])

        if self.context.main_block:
            yield SyntheticStatement("exit", "terminate", arguments=[])


    @property
    @memoize
    def flat_inner_nodes(self):
        return tuple(self._generate_flat_inner_nodes())

    def _generate_flat_inner_nodes(self):
        for s in self.statements:
            yield from s.intermediate_nodes

    def _get_first_requests(self):
        for s in self.statements:
            yield from s.first_requests
            if None not in s.first_requests:
                break
        else:
            yield None


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
        result = context.result()
        for n in self.children:
            result = result.merge(n.driver_run(context.extend(result)))
        return result

    def _get_reference_actions(self):
        for n in self.children:
            yield from n.reference_actions

    def _get_declaration_directions(self):
        for n in self.children:
            yield from n.declaration_directions

    def _describe_node(self):
        yield "block"
        for n in self.children:
            yield from self._indent_all(n.node_description)
