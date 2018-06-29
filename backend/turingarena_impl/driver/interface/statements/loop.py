import logging

from turingarena_impl.driver.interface.block import Block, BlockNode
from turingarena_impl.driver.interface.diagnostics import Diagnostic
from turingarena_impl.driver.interface.nodes import IntermediateNode, ExecutionResult
from turingarena_impl.driver.interface.statements.statement import Statement

logger = logging.getLogger(__name__)


class LoopStatement(Statement, IntermediateNode):
    __slots__ = []

    def _get_intermediate_nodes(self):
        yield self

    def _driver_run(self, context):
        while True:
            result = self.body_node.driver_run(context)
            if result.does_break:
                return result

    def _get_declaration_directions(self):
        return self.body_node.declaration_directions

    def _get_reference_actions(self):
        return []

    @property
    def body(self):
        return Block(ast=self.ast.body, context=self.context.with_loop())

    @property
    def body_node(self):
        return BlockNode.from_nodes(self.body.flat_inner_nodes)

    def expects_request(self, request):
        return self.body.expects_request(request)

    def validate(self):
        yield from self.body.validate()

    def _describe_node(self):
        yield "loop"
        yield from self._indent_all(self.body_node.node_description)


class BreakStatement(Statement, IntermediateNode):
    __slots__ = []

    def _get_intermediate_nodes(self):
        yield self

    def _driver_run(self, context):
        return context.result()._replace(does_break=True)

    def _get_reference_actions(self):
        return []

    def validate(self):
        if not self.context.in_loop:
            yield Diagnostic(Diagnostic.Messages.UNEXPECTED_BREAK, parseinfo=self.ast.parseinfo)
