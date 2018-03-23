import logging

from turingarena.interface.context import FunctionCallContext, AcceptCallbackContext
from turingarena.interface.driver.commands import CallbackReturn, FunctionCall
from turingarena.interface.exceptions import InterfaceError, FunctionCallError, FunctionNotDeclaredError
from turingarena.interface.executable import ImperativeStatement, Instruction
from turingarena.interface.expressions import Expression
from turingarena.interface.io import read_line

logger = logging.getLogger(__name__)


class CallStatement(ImperativeStatement):
    __slots__ = []

    @staticmethod
    def compile(ast):
        return CallStatement(ast=ast)

    @property
    def function_name(self):
        return self.ast.function_name

    @property
    def parameters(self):
        return [Expression.compile(p) for p in self.ast.parameters]

    @property
    def return_value(self):
        if self.ast.return_value is None:
            return None
        else:
            return Expression.compile(self.ast.return_value)

    def function(self, context):
        try:
            return context.global_context.functions[self.ast.function_name]
        except KeyError:
            raise FunctionNotDeclaredError(
                f"function {self.ast.function_name} is not defined",
                parseinfo=self.ast.parseinfo,
            ) from None

    def validate(self, context):
        self.validate_parameters(context)
        self.validate_return_value(context)

    def validate_parameters(self, context):
        fun = self.function(context)
        if len(self.parameters) != len(fun.signature.parameters):
            raise FunctionCallError(
                f"function {fun.name} "
                f"expects {len(fun.signature.parameters)} argument(s), "
                f"got {len(self.parameters)}",
                parseinfo=self.ast.parseinfo,
            )
        for parameter, expression in zip(fun.signature.parameters, self.parameters):
            expr_value_type = expression.value_type(declared_variables=context.variables)

            if expr_value_type != parameter.value_type:
                raise InterfaceError(
                    f"argument {parameter.name} "
                    f"of function {fun.name}: "
                    f"expected {parameter.value_type}, "
                    f"got {expr_value_type}",
                    parseinfo=expression.ast.parseinfo,
                )

    def validate_return_value(self, context):
        fun = self.function(context)
        return_type = fun.signature.return_type
        if return_type is not None and self.return_value is None:
            raise FunctionCallError(
                f"function {fun.name} returns {return_type}, but no return expression given",
                parseinfo=self.ast.parseinfo,
            )
        if return_type is None and self.return_value is not None:
            raise FunctionCallError(
                f"function {fun.name} does not return a value",
                parseinfo=self.ast.return_value.parseinfo,
            )
        return_expression_type = self.return_value and self.return_value.value_type(
            declared_variables=context.variables,
        )
        if self.return_value is not None and return_expression_type != return_type:
            raise FunctionCallError(
                f"function {fun.name} returns {return_type}, "
                f"but return expression is {return_expression_type}",
                parseinfo=self.ast.return_value.parseinfo,
            )

    def expects_request(self, request):
        return (
            request is not None
            and request.request_type == "function_call"
            and request.function_name == self.function_name
        )

    def check_variables(self, initialized_variables, allocated_variables):
        for exp in self.parameters:
            exp.check_variable(initialized_variables, allocated_variables)
        if self.return_value:
            self.return_value.check_variables(initialized_variables, allocated_variables)

    def initialized_variables(self):
        return [self.return_value]

    def generate_instructions(self, context):
        interface = context.procedure.global_context.interface
        call_context = FunctionCallContext(local_context=context)

        function = interface.functions[self.function_name]

        yield FunctionCallInstruction(
            statement=self,
            context=call_context,
            function=function,
        )

        if interface.signature.callbacks:
            yield from self.unroll_callbacks(call_context)

        yield FunctionReturnInstruction(
            statement=self,
            context=call_context,
            function=function,
        )

    def unroll_callbacks(self, call_context):
        while True:
            context = AcceptCallbackContext(call_context)
            yield AcceptCallbackInstruction(context=context)
            if context.callback is None:
                break

            yield from context.callback.generate_instructions(context)


class FunctionCallInstruction(Instruction):
    __slots__ = ["statement", "context", "function"]

    def on_request_lookahead(self, request):
        fun = self.function
        parameters = self.statement.parameters

        if not isinstance(request, FunctionCall):
            raise InterfaceError(f"expected call to '{fun.name}', got {request}")

        if request.function_name != fun.name:
            raise InterfaceError(f"expected call to '{fun.name}', got call to '{request.function_name}'")

        for value_expr, value in zip(parameters, request.parameters):
            value_type = value_expr.value_type(
                declared_variables=self.context.local_context.variables,
            )
            value_expr.evaluate_in(self.context.local_context).resolve(
                value_type.ensure(value)
            )

        self.context.accepted_callbacks = request.accepted_callbacks

    def should_send_input(self):
        return self.function.signature.return_type is not None


class FunctionReturnInstruction(Instruction):
    __slots__ = ["statement", "context", "function"]

    def on_generate_response(self):
        if self.function.signature.return_type:
            return_value = self.statement.return_value.evaluate_in(self.context.local_context).get()
            return_response = [1, return_value]
        else:
            return_response = [0]
        return (
            [0] +  # no more callbacks
            return_response
        )


class AcceptCallbackInstruction(Instruction):
    __slots__ = ["context"]

    def should_send_input(self):
        return True

    def on_communicate_with_process(self, connection):
        connection.downward.flush()
        callback_name = read_line(connection.upward).strip()
        if callback_name == "return":
            self.context.callback = None
        else:
            interface = self.context.call_context.local_context.procedure.global_context.interface
            self.context.callback = interface.callbacks[callback_name]


class ReturnStatement(ImperativeStatement):
    __slots__ = []

    @property
    def value(self):
        return Expression.compile(self.ast.value)

    def generate_instructions(self, context):
        yield ReturnInstruction(value=self.value, context=context)


class ReturnInstruction(Instruction):
    __slots__ = ["value", "context"]

    def on_request_lookahead(self, request):
        assert isinstance(request, CallbackReturn)
        self.value.evaluate_in(self.context).resolve(
            self.value.value_type(
                declared_variables=self.context.variables,
            ).ensure(request.return_value)
        )
