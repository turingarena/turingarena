import logging

from turingarena_impl.driver.interface.block import Block, BlockNode
from turingarena_impl.driver.interface.expressions import Expression
from turingarena_impl.driver.interface.nodes import IntermediateNode, StatementIntermediateNode, RequestLookaheadNode
from turingarena_impl.driver.interface.statements.statement import Statement
from turingarena_impl.driver.interface.variables import ReferenceStatus

logger = logging.getLogger(__name__)


class IfStatement(Statement, IntermediateNode):
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

    @property
    def then_node(self):
        return BlockNode.from_nodes(self.then_body.flat_inner_nodes)

    @property
    def else_node(self):
        if self.else_body is None:
            return None
        return BlockNode.from_nodes(self.else_body.flat_inner_nodes)

    def validate(self):
        yield from self.condition.validate()
        yield from self.then_body.validate()
        if self.else_body is not None:
            yield from self.else_body.validate()

    def _needs_request_lookahead(self):
        return not self.condition.is_status(ReferenceStatus.RESOLVED)

    def _get_intermediate_nodes(self):
        if self._needs_request_lookahead():
            yield RequestLookaheadNode()
            yield ResolveIfNode(self)
        yield self

    def _get_declaration_directions(self):
        yield from self.then_node.declaration_directions
        if self.else_node is not None:
            yield from self.else_node.declaration_directions

    def _get_first_requests(self):
        yield from self.then_body.first_requests
        if self.else_body is not None:
            yield from self.else_body.first_requests
        else:
            yield None

    def _driver_run(self, context):
        condition_value = self.condition.evaluate(context.bindings)
        if condition_value:
            return self.then_node.driver_run(context)
        elif self.else_node is not None:
            return self.else_node.driver_run(context)

    def _describe_node(self):
        yield f"if {self.condition}"
        yield from self._indent_all(self.then_node.node_description)
        if self.else_node is not None:
            yield "else"
            yield from self._indent_all(self.else_node.node_description)


class ResolveIfNode(StatementIntermediateNode):
    def _get_conditions_expecting(self, request):
        if request in self.statement.then_body.first_requests:
            yield 1
        if self.statement.else_body is not None:
            if request in self.statement.else_body.first_requests:
                yield 0

    def _get_conditions_expecting_no_request(self):
        yield from self._get_conditions_expecting(None)
        if self.statement.else_body is None:
            yield 0

    def _driver_run(self, context):
        if context.phase is ReferenceStatus.RESOLVED:
            return context.result()._replace(assignments=list(self._get_assignments(context)))

    def _get_assignments(self, context):
        logger.debug(f"request_lookahead: {context.request_lookahead}")
        matching_conditions = frozenset(self._get_conditions_expecting(context.request_lookahead))
        logger.debug(f"matching_conditions1: {matching_conditions}")
        if not matching_conditions:
            matching_conditions = frozenset(self._get_conditions_expecting_no_request())
            logger.debug(f"matching_conditions2: {matching_conditions}")
        [condition_value] = matching_conditions
        yield self.statement.condition.reference, condition_value

    def _describe_node(self):
        yield "resolve if"
