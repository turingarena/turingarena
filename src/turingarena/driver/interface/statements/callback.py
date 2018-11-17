import logging
from abc import abstractmethod
from collections import namedtuple

from turingarena.driver.client.exceptions import InterfaceError
from turingarena.driver.interface.block import Block, AbstractBlock
from turingarena.driver.interface.callables import CallbackPrototype
from turingarena.driver.interface.exceptions import InterfaceExitReached
from turingarena.driver.interface.execution import RequestSignature
from turingarena.driver.interface.expressions import Expression, IntLiteralExpressionSynthetic
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.phase import ExecutionPhase
from turingarena.driver.interface.statements.io import OutputStatement
from turingarena.driver.interface.statements.statement import Statement
from turingarena.driver.interface.variables import ReferenceAction, ReferenceStatus, ReferenceDirection

logger = logging.getLogger(__name__)


class CallbackRequestOutputStatement(OutputStatement):
    @property
    def arguments(self):
        return [IntLiteralExpressionSynthetic(value=1)]

    def _get_comment(self):
        return "requesting a callback"


class CallbackIndexOutputStatement(namedtuple("CallbackWriteIndexNode", ["implementation"]), OutputStatement):
    @property
    def callback_index(self):
        return self.implementation.context.callback_index

    @property
    def arguments(self):
        return [IntLiteralExpressionSynthetic(value=self.callback_index)]

    def _get_comment(self):
        return f"index of this callback: {self.callback_index} = {self.implementation.name}"


class CallbackBody(AbstractBlock):
    def __init__(self, implementation):
        self.implementation = implementation

    def _generate_flat_inner_nodes(self):
        yield CallbackCallNode(self.implementation)
        yield CallbackRequestOutputStatement()
        yield CallbackIndexOutputStatement(self.implementation)

        yield from self.implementation.raw_body.flat_inner_nodes

        if not self.implementation.has_return_value:
            yield CallbackEndNode(callback=self.implementation)


class CallbackImplementation(IntermediateNode, CallbackPrototype):
    __slots__ = []

    @property
    def raw_body(self):
        inner_context = self.context.local_context.with_reference_actions(
            ReferenceAction(reference=p.as_reference(), status=ReferenceStatus.DECLARED)
            for p in self.parameters
        )
        return Block(
            ast=self.ast.body if self.ast.body else self.default_body,
            context=inner_context,
        )

    @property
    def body(self):
        return CallbackBody(self)

    @property
    def default_body(self):
        fake_ast_body = [
            namedtuple("write", ["statement_type", "arguments"])("write", [
                namedtuple("expression", ["expression_type", "variable_name", "indices"])("reference_subscript", p.name,
                                                                                          "")
                for p in self.parameters
            ])
        ]
        if self.has_return_value:
            return_var = namedtuple("expression", ["expression_type", "variable_name", "indices"])(
                "reference_subscript", "_result", "")
            fake_ast_body += [
                namedtuple("read", ["statement_type", "arguments"])("read", [return_var]),
                namedtuple("ret", ["statement_type", "value"])("return", return_var),
            ]
        return namedtuple("body", ["statements"])(fake_ast_body)

    def validate(self):
        yield from self.prototype.validate()

    def _driver_run(self, context):
        assert context.phase is None
        context.report_ready()
        context.send_driver_upward(1)  # has callbacks
        context.send_driver_upward(self.context.callback_index)
        self.body.driver_run(context)

    def _get_declaration_directions(self):
        return self.body.declaration_directions


class CallbackCallNode(IntermediateNode, namedtuple("CallbackCallNode", [
    "callback_implementation",
])):
    def _get_reference_actions(self):
        for p in self.callback_implementation.parameters:
            yield ReferenceAction(reference=p.as_reference(), status=ReferenceStatus.DECLARED)

    def _get_declaration_directions(self):
        yield ReferenceDirection.UPWARD

    def _driver_run(self, context):
        if context.phase is ExecutionPhase.REQUEST:
            for p in self.callback_implementation.parameters:
                r = p.as_reference()
                value = context.bindings[r]
                context.send_driver_upward(value)

    def _describe_node(self):
        yield "callback_call"


class AbstractCallbackReturnNode(IntermediateNode):
    def _needs_request_lookahead(self):
        return True

    def _driver_run(self, context):
        if context.phase is ExecutionPhase.REQUEST:
            request = context.request_lookahead
            command = request.command
            if not command == "callback_return":
                raise InterfaceError(f"expecting 'callback_return', got '{command}'")

            return context.result()._replace(
                assignments=list(self._get_assignments(context))
            )

    @abstractmethod
    def _has_return_value(self):
        pass

    def _get_assignments(self, context):
        has_return_value = bool(int(context.receive_driver_downward()))

        if not has_return_value and self._has_return_value():
            raise InterfaceError(
                f"callback is a function, "
                f"but the provided implementation did not return anything"
            )

        if has_return_value and not self._has_return_value():
            raise InterfaceError(
                f"callback is a procedure, "
                f"but the provided implementation returned something"
            )

        yield from self._do_get_assignments(context)

    def _do_get_assignments(self, context):
        return []


class ReturnStatement(AbstractCallbackReturnNode, Statement):
    __slots__ = []

    def _has_return_value(self):
        return True

    def _do_get_assignments(self, context):
        value = int(context.receive_driver_downward())
        yield self.value.reference, value

    @property
    def value(self):
        return Expression.compile(self.ast.value, self.context.expression(reference=True))

    def validate(self):
        yield from self.value.validate()

    def _get_reference_actions(self):
        yield ReferenceAction(reference=self.value.reference, status=ReferenceStatus.RESOLVED)

    def _describe_node(self):
        yield f"callback return"


class CallbackEndNode(AbstractCallbackReturnNode, namedtuple("CallbackEndNode", ["callback"])):
    def _has_return_value(self):
        return False

    def _describe_node(self):
        yield f"callback end"


class ExitStatement(IntermediateNode):
    __slots__ = []


class ExitStatementAst(ExitStatement, Statement, IntermediateNode):
    __slots__ = []

    def _get_intermediate_nodes(self):
        yield self

    def _needs_request_lookahead(self):
        return True

    def validate(self):
        # TODO: check that exit is used only in valid places
        return []

    def _get_first_requests(self):
        yield RequestSignature("exit")

    def _get_reference_actions(self):
        return []

    def _driver_run(self, context):
        if context.phase is ExecutionPhase.REQUEST:
            command = context.request_lookahead.command
            if command != "exit":
                raise InterfaceError(f"Expecting exit, got {command}")
            raise InterfaceExitReached

    @property
    def does_break(self):
        return True
