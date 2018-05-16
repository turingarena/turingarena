import logging
from collections import namedtuple

from turingarena import InterfaceError
from turingarena.driver.commands import CallbackReturn, FunctionCall
from turingarena_impl.interface.callables import Callback
from turingarena_impl.interface.common import Instruction
from turingarena_impl.interface.context import StaticCallbackBlockContext
from turingarena_impl.interface.exceptions import Diagnostic
from turingarena_impl.interface.expressions import Expression
from turingarena_impl.interface.statements.io import read_line, do_flush
from turingarena_impl.interface.statements.statement import Statement
from turingarena_impl.interface.variables import Variable, TypeExpression, VariableDeclaration

logger = logging.getLogger(__name__)


class CallStatement(Statement):
    __slots__ = []

    @property
    def function_name(self):
        return self.ast.name

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

    @property
    def function(self):
        return self.context.global_context.function_map[self.function_name]

    @property
    def callbacks(self):
        return tuple(
            next(
                Callback(ast=c, context=StaticCallbackBlockContext(
                    local_context=self.context,
                    callback_index=i,
                ))
                for c in self.ast.callbacks
                if c.prototype.name == s.name
            )
            for i, s in enumerate(self.function.callbacks_signature)
        )

    @property
    def has_callbacks(self):
        return self.callbacks is not None

    def validate(self):
        if self.function_name not in self.context.global_context.function_map:
            yield Diagnostic(
                Diagnostic.Messages.FUNCTION_NOT_DECLARED,
                self.function_name,
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
                value_type=TypeExpression.value_type_dimensions(len(return_value_ast.indices)),
            )
            return self.context.with_variables((var,))
        else:
            return self.context

    def validate_parameters(self):
        fun = self.function
        if len(self.parameters) != len(fun.parameters):
            yield Diagnostic(
                Diagnostic.Messages.CALL_WRONG_ARGS_NUMBER,
                fun.name, len(fun.parameters), len(self.parameters),
                parseinfo=self.ast.parseinfo,
            )
        for parameter, expression in zip(fun.parameters, self.parameters):
            expr_value_type = expression.value_type

            if str(expr_value_type) != str(parameter.value_type):
                yield Diagnostic(
                    Diagnostic.Messages.CALL_WRONG_ARGS_TYPE,
                    parameter.name, fun.name, parameter.value_type, expr_value_type,
                    parseinfo=expression.ast.parseinfo,
                )

            yield from expression.validate()

    def validate_return_value(self):
        if self.return_value is not None:
            yield from self.return_value.validate(lvalue=True)
        if self.function.has_return_value and self.return_value is None:
            yield Diagnostic(
                Diagnostic.Messages.CALL_NO_RETURN_EXPRESSION, self.function.name,
                parseinfo=self.ast.parseinfo,
            )
        if not self.function.has_return_value and self.return_value is not None:
            yield Diagnostic(
                Diagnostic.Messages.FUNCTION_DOES_NOT_RETURN_VALUE, self.function.name,
                parseinfo=self.ast.return_value.parseinfo,
            )

    def expects_request(self, request):
        return (
            request is not None
            and isinstance(request, FunctionCall)
            and request.function_name == self.function_name
        )

    @property
    def may_process_requests(self):
        return True

    def generate_instructions(self, bindings):
        function = self.context.global_context.function_map[self.function_name]

        yield FunctionCallInstruction(
            statement=self,
            bindings=bindings,
        )

        if function.has_callbacks:
            yield from self.unroll_callbacks(bindings)

        yield FunctionReturnInstruction(
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


class FunctionCallInstruction(Instruction, namedtuple("FunctionCallInstruction", [
    "statement", "bindings"
])):
    __slots__ = []

    def on_request_lookahead(self, request):
        fun = self.statement.function
        parameters = self.statement.parameters

        if not isinstance(request, FunctionCall):
            raise InterfaceError(f"expected call to '{fun.name}', got {request}")

        if request.function_name != fun.name:
            raise InterfaceError(f"expected call to '{fun.name}', got call to '{request.function_name}'")

        if len(request.parameters) != len(fun.parameters):
            raise InterfaceError(
                f"'{fun.name}' expects {len(fun.parameters)} arguments, "
                f"got {len(request.parameters)}"
            )

        for value_expr, value in zip(parameters, request.parameters):
            if value_expr.is_assignable():
                value_expr.assign(self.bindings, value)

    def should_send_input(self):
        return self.statement.function.has_return_value


class FunctionReturnInstruction(Instruction, namedtuple("FunctionReturnInstruction", [
    "statement", "bindings"
])):
    __slots__ = []

    def on_generate_response(self):
        if self.statement.function.has_return_value:
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

    def on_communicate_with_process(self, connection):
        do_flush(connection)
        has_callback = int(read_line(connection.upward).strip())
        if has_callback:
            callback_index = int(read_line(connection.upward).strip())
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
