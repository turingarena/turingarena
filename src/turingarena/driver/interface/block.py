import logging
from collections import namedtuple

from turingarena.driver.interface.common import ImperativeStructure, AbstractSyntaxNodeWrapper, memoize
from turingarena.driver.interface.diagnostics import Diagnostic
from turingarena.driver.interface.expressions import SyntheticExpression
from turingarena.driver.interface.seq import SequenceNode
from turingarena.driver.interface.statements.io import InitialCheckpointNode
from turingarena.driver.interface.statements.statement import SyntheticStatement, Statement
from turingarena.driver.interface.step import Step

logger = logging.getLogger(__name__)


class Block(ImperativeStructure, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    @memoize
    def statements(self):
        return tuple(self._generate_statements())

    def _generate_statements(self):
        for node in self.flat_inner_nodes:
            if isinstance(node, Statement):
                yield node

    @property
    @memoize
    def flat_inner_nodes(self):
        return tuple(self._generate_flat_inner_nodes())

    def _generate_flat_inner_nodes(self):
        if self.context.main_block:
            yield InitialCheckpointNode()

        inner_context = self.context._replace(main_block=False)
        for s in self.ast.statements:
            from turingarena.driver.interface.statements.statements import statement_classes
            for cls in statement_classes[s.statement_type]:
                node = cls(s, inner_context)
                if not node.is_relevant:
                    continue
                yield node
                inner_context = inner_context.with_reference_actions(node.reference_actions)

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
        return self.flat_inner_nodes

    def _generate_synthetic_statements(self):
        for s in self.statements:
            yield s
            if s.statement_type == "call" and s.method.has_callbacks:
                yield SyntheticStatement("write", "no more callbacks", arguments=[
                    SyntheticExpression("int_literal", value=0),
                ])

        if self.context.main_block:
            yield SyntheticStatement("exit", "terminate", arguments=[])


class BlockNode(SequenceNode, namedtuple("BlockNode", ["children"])):
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

    def _describe_node(self):
        yield "block"
        for n in self.children:
            yield from self._indent_all(n.node_description)
