import logging

from turingarena.driver.interface.block import Block
from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena.driver.interface.expressions import Expression
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.control import ControlStructure
from turingarena.driver.interface.statements.statement import Statement

logger = logging.getLogger(__name__)


class AbstractIfNode(IntermediateNode, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def condition(self):
        return Expression.compile(self.ast.condition)

    @property
    def branches(self):
        return tuple(
            b
            for b in (self.then_body, self.else_body)
            if b is not None
        )

    @property
    def then_body(self):
        return Block(ast=self.ast.then_body, context=self.context)

    @property
    def else_body(self):
        if self.ast.else_body is not None:
            return Block(ast=self.ast.else_body, context=self.context)
        else:
            return None


class If(ControlStructure, AbstractIfNode, Statement):
    def _get_bodies(self):
        yield self.then_body
        if self.else_body is not None:
            yield self.else_body

    def _describe_node(self):
        yield f"if {self.condition}"
        yield from self._indent_all(self.then_body.node_description)
        if self.else_body is not None:
            yield "else"
            yield from self._indent_all(self.else_body.node_description)


class IfConditionResolve(AbstractIfNode):
    def _get_conditions_expecting(self, request):
        if request in self.context.first_requests(self.then_body):
            yield 1
        if self.else_body is not None:
            if request in self.context.first_requests(self.else_body):
                yield 0

    def _get_conditions_expecting_no_request(self):
        yield from self._get_conditions_expecting(None)
        if self.else_body is None:
            yield 0

    def get_conditions(self, request):
        logger.debug(f"request_lookahead: {request}")
        matching_conditions = frozenset(self._get_conditions_expecting(request))
        logger.debug(f"matching_conditions1: {matching_conditions}")
        if not matching_conditions:
            matching_conditions = frozenset(self._get_conditions_expecting_no_request())
            logger.debug(f"matching_conditions2: {matching_conditions}")
        return matching_conditions

    def _describe_node(self):
        yield "resolve if"
