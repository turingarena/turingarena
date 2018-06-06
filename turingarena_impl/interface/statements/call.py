import logging
from collections import namedtuple

from turingarena import InterfaceError
from turingarena.driver.commands import CallbackReturn, MethodCall
from turingarena_impl.interface.callables import CallbackImplementation
from turingarena_impl.interface.context import StaticCallbackBlockContext
from turingarena_impl.interface.diagnostics import Diagnostic
from turingarena_impl.interface.expressions import Expression
from turingarena_impl.interface.nodes import IntermediateNode, StatementIntermediateNode
from turingarena_impl.interface.statements.statement import Statement
from turingarena_impl.interface.variables import ReferenceStatus, ReferenceDirection, ReferenceAction

logger = logging.getLogger(__name__)


class CallStatement(Statement):
    __slots__ = []

    @property
    def method_name(self):
        return self.ast.name

    @property
    def method(self):
        return self.context.global_context.methods_by_name[self.method_name]

    @property
    def parameters(self):
        return [Expression.compile(p, self.context) for p in self.ast.parameters]

    @property
    def return_value(self):
        if self.ast.return_value:
            return Expression.compile(self.ast.return_value, self.context)
        else:
            return None

    def find_callback_implementation(self, index, callback):
        return next(
            CallbackImplementation(ast=implementation, context=StaticCallbackBlockContext(
                local_context=self.context,
                callback_index=index,
            ))
            for implementation in self.ast.callbacks
            if implementation.declarator.name == callback.name
        )

    @property
    def callbacks(self):
        return [
            self.find_callback_implementation(i, s)
            for i, s in enumerate(self.method.callbacks)
        ]

    def validate(self):
        if self.method_name not in self.context.global_context.methods_by_name:
            yield Diagnostic(
                Diagnostic.Messages.METHOD_NOT_DECLARED,
                self.method_name,
                parseinfo=self.ast.parseinfo,
            )
        else:
            yield from self.validate_parameters_resolved()
            yield from self.validate_parameters()
            yield from self.validate_return_value()

    def validate_parameters_resolved(self):
        for p in self.parameters:
            if p.reference is not None:
                continue
            yield from p.validate_resolved()

    def validate_parameters(self):
        method = self.method
        if len(self.parameters) != len(method.parameters):
            yield Diagnostic(
                Diagnostic.Messages.CALL_WRONG_ARGS_NUMBER,
                method.name, len(method.parameters), len(self.parameters),
                parseinfo=self.ast.parseinfo,
            )
        for parameter, expression in zip(method.parameters, self.parameters):
            yield from expression.validate()
            if expression.dimensions != parameter.dimensions:
                yield Diagnostic(
                    Diagnostic.Messages.CALL_WRONG_ARGS_TYPE,
                    parameter.name, method.name, parameter.dimensions, expression.dimensions,
                    parseinfo=expression.ast.parseinfo,
                )

    def validate_return_value(self):
        method = self.method
        if self.return_value is not None:
            yield from self.return_value.validate_reference()
        if method.has_return_value and self.return_value is None:
            yield Diagnostic(
                Diagnostic.Messages.CALL_NO_RETURN_EXPRESSION, method.name,
                parseinfo=self.ast.parseinfo,
            )
        if not method.has_return_value and self.return_value is not None:
            yield Diagnostic(
                Diagnostic.Messages.METHOD_DOES_NOT_RETURN_VALUE, method.name,
                parseinfo=self.ast.return_value.parseinfo,
            )

    def expects_request(self, request):
        return (
            request is not None
            and isinstance(request, MethodCall)
            and request.method_name == self.method_name
        )

    @property
    def may_process_requests(self):
        return True

    def _get_intermediate_nodes(self):
        yield MethodCallInstruction(self)

        if self.method.has_callbacks:
            yield MethodCallbacksInstruction(self)

        if self.method.has_return_value:
            yield MethodReturnInstruction(self)

    def generate_instructions(self, bindings):
        method = self.method

        yield MethodCallInstruction(
            statement=self,
            bindings=bindings,
        )

        if method.has_callbacks:
            yield from self.unroll_callbacks(bindings)

        yield MethodReturnInstruction(
            statement=self,
            bindings=bindings,
        )

    def unroll_callbacks(self, bindings):
        while True:
            accepted_callback_holder = []
            yield AcceptCallbackNode(bindings=bindings, accepted_callback_holder=accepted_callback_holder)
            if accepted_callback_holder:
                [accepted_callback_index] = accepted_callback_holder
                callback = self.callbacks[accepted_callback_index]
                yield from callback.generate_instructions(bindings)
            else:
                break


class MethodCallInstruction(StatementIntermediateNode):
    __slots__ = []

    def _get_direction(self):
        return ReferenceDirection.DOWNWARD

    def _get_reference_actions(self):
        references = self.statement.context.get_references(ReferenceStatus.RESOLVED)
        for p in self.statement.parameters:
            if p.reference is not None and p.reference not in references:
                yield ReferenceAction(p.reference, ReferenceStatus.RESOLVED)

    def on_request_lookahead(self, request):
        method = self.statement.method
        parameters = self.statement.parameters

        if not isinstance(request, MethodCall):
            raise InterfaceError(f"expected call to '{method.name}', got {request}")

        if request.method_name != method.name:
            raise InterfaceError(f"expected call to '{method.name}', got call to '{request.method_name}'")

        if len(request.parameters) != len(method.parameters):
            raise InterfaceError(
                f"'{method.name}' expects {len(method.parameters)} arguments, "
                f"got {len(request.parameters)}"
            )

        for value_expr, value in zip(parameters, request.parameters):
            if value_expr.is_assignable():
                value_expr.assign(self.bindings, value)

    def should_send_input(self):
        return self.statement.method.has_return_value


class MethodReturnInstruction(StatementIntermediateNode):
    __slots__ = []

    def _get_direction(self):
        return ReferenceDirection.UPWARD

    def _get_reference_actions(self):
        yield ReferenceAction(self.statement.return_value.reference, ReferenceStatus.DECLARED)

    def on_generate_response(self):
        if self.statement.method.has_return_value:
            return_value = self.statement.return_value.evaluate(self.bindings)
            return_response = [1, return_value]
        else:
            return_response = [0]
        return (
            [0] +  # no more callbacks
            return_response
        )


class AcceptCallbackNode(IntermediateNode, namedtuple("AcceptCallbackNode", [
    "bindings", "accepted_callback_holder"
])):
    __slots__ = []

    def should_send_input(self):
        return True

    def has_upward(self):
        return True

    def on_communicate_upward(self, lines):
        [has_callback] = next(lines)
        if has_callback:
            [callback_index] = next(lines)
            self.accepted_callback_holder[:] = [callback_index]


class ReturnStatement(Statement):
    __slots__ = []

    @property
    def value(self):
        return Expression.compile(self.ast.value, self.context)

    def generate_instructions(self, bindings):
        yield ReturnNode(value=self.value, bindings=bindings)

    def validate(self):
        yield from self.value.validate()


class ReturnNode(IntermediateNode, namedtuple("ReturnNode", [
    "value", "bindings"
])):
    __slots__ = []

    def on_request_lookahead(self, request):
        assert isinstance(request, CallbackReturn)
        assert self.value.is_assignable()
        self.value.assign(self.bindings, request.return_value)
