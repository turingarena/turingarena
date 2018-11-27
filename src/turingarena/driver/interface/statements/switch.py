import logging
import warnings

from turingarena.driver.interface.block import Block
from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena.driver.interface.expressions import Expression
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.control import ControlStructure
from turingarena.driver.interface.statements.statement import Statement

logger = logging.getLogger(__name__)


class SwitchNode(IntermediateNode, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def cases(self):
        return tuple(self._get_cases())

    def _get_cases(self):
        for case in self.ast.cases:
            # FIXME: .with_reference_actions(<resolve node>.reference_actions)
            yield Case(ast=case, context=self.context)

    @property
    def value(self):
        return Expression.compile(self.ast.value)


class Switch(ControlStructure, SwitchNode, Statement):
    __slots__ = []

    def _get_bodies(self):
        for c in self.cases:
            yield c.body

    def _describe_node(self):
        yield f"switch {self.value} "
        for c in self.cases:
            yield from self._indent_all(self._describe_case(c))

    def _describe_case(self, case):
        labels = ", ".join(str(l.value) for l in case.labels)
        yield f"case {labels}"
        yield from self._indent_all(case.body.node_description)


class Case(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def body(self):
        return Block(ast=self.ast.body, context=self.context)

    @property
    def labels(self):
        return [
            Expression.compile(l)
            for l in self.ast.labels
        ]


class SwitchValueResolve(SwitchNode):
    def _describe_node(self):
        yield f"resolve {self}"
