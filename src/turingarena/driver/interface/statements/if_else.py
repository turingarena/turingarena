import logging

from turingarena.driver.interface.block import Block
from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena.driver.interface.evalexpression import evaluate_expression, ExpressionStatusAnalyzer
from turingarena.driver.interface.expressions import Expression
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.phase import ExecutionPhase
from turingarena.driver.interface.statements.statement import Statement
from turingarena.driver.interface.variables import ReferenceStatus

logger = logging.getLogger(__name__)


class AbstractIfNode(IntermediateNode, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def condition(self):
        return Expression.compile(self.ast.condition, self.context.expression())

    @property
    def then_body(self):
        return Block(ast=self.ast.then_body, context=self.context)

    @property
    def else_body(self):
        if self.ast.else_body is not None:
            return Block(ast=self.ast.else_body, context=self.context)
        else:
            return None

    def validate(self):
        yield from self.condition.validate()
        yield from self.then_body.validate()
        if self.else_body is not None:
            yield from self.else_body.validate()


class If(AbstractIfNode, Statement):
    def _get_declaration_directions(self):
        yield from self.then_body.declaration_directions
        if self.else_body is not None:
            yield from self.else_body.declaration_directions

    def _get_first_requests(self):
        yield from self.then_body.first_requests
        if self.else_body is not None:
            yield from self.else_body.first_requests
        else:
            yield None

    def _driver_run(self, context):
        condition_value = evaluate_expression(self.condition, context.bindings)
        if condition_value:
            return self.then_body.driver_run(context)
        elif self.else_body is not None:
            return self.else_body.driver_run(context)

    def _describe_node(self):
        yield f"if {self.condition}"
        yield from self._indent_all(self.then_body.node_description)
        if self.else_body is not None:
            yield "else"
            yield from self._indent_all(self.else_body.node_description)


class ResolveIfNode(AbstractIfNode):
    def _is_already_resolved(self):
        return ExpressionStatusAnalyzer(self.context, ReferenceStatus.RESOLVED).visit(self.condition)

    def _is_relevant(self):
        return not self._is_already_resolved()

    def _get_conditions_expecting(self, request):
        if request in self.then_body.first_requests:
            yield 1
        if self.else_body is not None:
            if request in self.else_body.first_requests:
                yield 0

    def _get_conditions_expecting_no_request(self):
        yield from self._get_conditions_expecting(None)
        if self.else_body is None:
            yield 0

    def _driver_run(self, context):
        if context.phase is ExecutionPhase.REQUEST:
            return context.result()._replace(assignments=list(self._get_assignments(context)))

    def _get_assignments(self, context):
        logger.debug(f"request_lookahead: {context.request_lookahead}")
        matching_conditions = frozenset(self._get_conditions_expecting(context.request_lookahead))
        logger.debug(f"matching_conditions1: {matching_conditions}")
        if not matching_conditions:
            matching_conditions = frozenset(self._get_conditions_expecting_no_request())
            logger.debug(f"matching_conditions2: {matching_conditions}")
        [condition_value] = matching_conditions
        yield self.condition.reference, condition_value

    def _needs_request_lookahead(self):
        return True

    def _describe_node(self):
        yield "resolve if"
