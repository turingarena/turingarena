import logging

from turingarena.interface.context import FunctionCallContext, AcceptCallbackContext
from turingarena.interface.driver.commands import CallbackReturn, FunctionCall
from turingarena.interface.exceptions import InterfaceError, FunctionCallError, FunctionNotDeclaredError
from turingarena.interface.executable import ImperativeStatement, Instruction
from turingarena.interface.expressions import Expression
from turingarena.interface.io import read_line

logger = logging.getLogger(__name__)


class CallStatement(ImperativeStatement):
    __slots__ = ["function", "parameters", "return_value"]

    @staticmethod
    def compile_parameter(ast, *, fun, decl, scope):
        expr = Expression.compile(ast)

        expr_value_type = expr.value_type(declared_variables=scope.variables)

        if expr_value_type != decl.value_type:
            raise InterfaceError(
                f"argument {decl.name} "
                f"of function {fun.name}: "
                f"expected {decl.value_type}, "
                f"got {expr_value_type}",
                parseinfo=ast.parseinfo,
            )
        return expr

    @staticmethod
    def compile(ast, scope):
        try:
            fun = scope.functions[ast.function_name]
        except KeyError:
            raise FunctionNotDeclaredError(
                f"function {ast.function_name} is not defined",
                parseinfo=ast.parseinfo,
            ) from None

        if len(ast.parameters) != len(fun.signature.parameters):
            raise FunctionCallError(
                f"function {fun.name} "
                f"expects {len(fun.signature.parameters)} argument(s), "
                f"got {len(ast.parameters)}",
                parseinfo=ast.parseinfo,
            )

        parameters = [
            CallStatement.compile_parameter(param_ast, fun=fun, decl=decl, scope=scope)
            for decl, param_ast in
            zip(fun.signature.parameters, ast.parameters)
        ]

        return_value = CallStatement.compile_return_value(ast.return_value, fun=fun, scope=scope)

        return_type = fun.signature.return_type
        if return_type is not None and return_value is None:
            raise FunctionCallError(
                f"function {fun.name} returns {return_type}, but no return expression given",
                parseinfo=ast.parseinfo,
            )

        if return_type is None and return_value is not None:
            raise FunctionCallError(
                f"function {fun.name} does not return a value",
                parseinfo=ast.return_value.parseinfo,
            )

        return_expression_type = return_value and return_value.value_type(
            declared_variables=scope.variables,
        )
        if return_value is not None and return_expression_type != return_type:
            raise FunctionCallError(
                f"function {fun.name} returns {return_type}, "
                f"but return expression is {return_expression_type}",
                parseinfo=ast.return_value.parseinfo,
            )

        return CallStatement(
            ast=ast,
            function=fun,
            parameters=parameters,
            return_value=return_value,
        )

    @staticmethod
    def compile_return_value(ast, *, fun, scope):
        if ast is None:
            return_value = None
        else:
            return_value = Expression.compile(ast)
        return return_value

    def first_calls(self):
        return {self.function.name}

    def check_variables(self, initialized_variables, allocated_variables):
        for exp in self.parameters:
            exp.check_variable(initialized_variables, allocated_variables)
        if self.return_value:
            self.return_value.check_variables(initialized_variables, allocated_variables)

    def initialized_variables(self):
        return [self.return_value]

    def generate_instructions(self, context):
        call_context = FunctionCallContext(local_context=context)

        yield FunctionCallInstruction(statement=self, context=call_context)

        if context.procedure.global_context.interface.signature.callbacks:
            yield from self.unroll_callbacks(call_context)

        yield FunctionReturnInstruction(statement=self, context=call_context)

    def unroll_callbacks(self, call_context):
        while True:
            context = AcceptCallbackContext(call_context)
            yield AcceptCallbackInstruction(context=context)
            if context.callback is None:
                break

            yield from context.callback.generate_instructions(context)


class FunctionCallInstruction(Instruction):
    __slots__ = ["statement", "context"]

    def on_request_lookahead(self, request):
        fun = self.statement.function
        parameters = self.statement.parameters

        if not isinstance(request, FunctionCall):
            raise InterfaceError(f"expected call to '{fun.name}', got {request}")

        if request.function_name != fun.name:
            raise InterfaceError(f"expected call to '{fun.name}', got call to '{request.function_name}'")

        for value_expr, value in zip(parameters, request.parameters):
            value_type = value_expr.value_type(
                declared_variables=self.context.local_context.scope.variables,
            )
            value_expr.evaluate_in(self.context.local_context).resolve(
                value_type.ensure(value)
            )

        self.context.accepted_callbacks = request.accepted_callbacks

    def should_send_input(self):
        has_return_type = (self.statement.function.signature.return_type is not None)
        return has_return_type


class FunctionReturnInstruction(Instruction):
    __slots__ = ["statement", "context"]

    def on_generate_response(self):
        if self.statement.function.signature.return_type:
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
            self.context.callback = interface.body.scope.callbacks[callback_name]


class ReturnStatement(ImperativeStatement):
    __slots__ = ["value"]

    @staticmethod
    def compile(ast, scope):
        return ReturnStatement(
            ast=ast,
            value=Expression.compile(ast.value),
        )

    def generate_instructions(self, context):
        yield ReturnInstruction(value=self.value, context=context)


class ReturnInstruction(Instruction):
    __slots__ = ["value", "context"]

    def on_request_lookahead(self, request):
        assert isinstance(request, CallbackReturn)
        self.value.evaluate_in(self.context).resolve(
            self.value.value_type(
                declared_variables=self.context.scope.variables,
            ).ensure(request.return_value)
        )
