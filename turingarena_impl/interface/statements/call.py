import logging
from collections import namedtuple

from turingarena import InterfaceError
from turingarena.driver.commands import CallbackReturn, MethodCall
from turingarena_impl.interface.callables import CallbackImplementation
from turingarena_impl.interface.common import Instruction
from turingarena_impl.interface.context import StaticCallbackBlockContext
from turingarena_impl.interface.diagnostics import Diagnostic
from turingarena_impl.interface.expressions import Expression
from turingarena_impl.interface.statements.statement import Statement
from turingarena_impl.interface.variables import Variable, VariableDeclaration

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
        return Expression.compile(self.ast.return_value, self.context_after) if self.ast.return_value else None

    @property
    def declared_variables(self):
        return (VariableDeclaration(
            name=self.return_value.variable_name,
            dimensions=len(self.return_value.indices),
            to_allocate=len(self.return_value.indices),
        ),) if self.return_value else ()

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
            yield from self.validate_parameters()
            yield from self.validate_return_value()

    @property
    def context_after(self):
        return_value_ast = self.ast.return_value
        if return_value_ast is not None:
            var = Variable(
                name=return_value_ast.variable_name,
                dimensions=len(return_value_ast.indices),
            )
            return self.context.with_variables((var,))
        else:
            return self.context

    def validate_parameters(self):
        method = self.method
        if len(self.parameters) != len(method.parameters):
            yield Diagnostic(
                Diagnostic.Messages.CALL_WRONG_ARGS_NUMBER,
                method.name, len(method.parameters), len(self.parameters),
                parseinfo=self.ast.parseinfo,
            )
        for parameter, expression in zip(method.parameters, self.parameters):
            if expression.dimensions != parameter.dimensions:
                yield Diagnostic(
                    Diagnostic.Messages.CALL_WRONG_ARGS_TYPE,
                    parameter.name, method.name, parameter.dimensions, expression.dimensions,
                    parseinfo=expression.ast.parseinfo,
                )

            yield from expression.validate()

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
            yield AcceptCallbackInstruction(bindings=bindings, accepted_callback_holder=accepted_callback_holder)
            if accepted_callback_holder:
                [accepted_callback_index] = accepted_callback_holder
                callback = self.callbacks[accepted_callback_index]
                yield from callback.generate_instructions(bindings)
            else:
                break


class MethodCallInstruction(Instruction, namedtuple("MethodCallInstruction", [
    "statement", "bindings"
])):
    __slots__ = []

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


class MethodReturnInstruction(Instruction, namedtuple("MethodReturnInstruction", [
    "statement", "bindings"
])):
    __slots__ = []

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


class AcceptCallbackInstruction(Instruction, namedtuple("AcceptCallbackInstruction", [
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
        yield ReturnInstruction(value=self.value, bindings=bindings)

    def validate(self):
        yield from self.value.validate()


class ReturnInstruction(Instruction, namedtuple("ReturnInstruction", [
    "value", "bindings"
])):
    __slots__ = []

    def on_request_lookahead(self, request):
        assert isinstance(request, CallbackReturn)
        assert self.value.is_assignable()
        self.value.assign(self.bindings, request.return_value)
