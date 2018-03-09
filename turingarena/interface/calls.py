import logging

from turingarena.interface.driver.commands import CallbackReturn, FunctionCall
from turingarena.interface.exceptions import InterfaceError
from turingarena.interface.executable import ImperativeStatement, Instruction
from turingarena.interface.expressions import Expression
from turingarena.interface.io import read_line

logger = logging.getLogger(__name__)


class FunctionCallContext:
    __slots__ = ["frame", "accepted_callbacks"]

    def __init__(self, frame):
        self.frame = frame


class AcceptCallbackContext:
    __slots__ = ["call", "callback"]

    def __init__(self, call):
        self.call = call
        self.callback = None


class CallbackContext:
    __slots__ = ["accept", "parameters"]


class CallStatement(ImperativeStatement):
    __slots__ = ["function", "parameters", "return_value"]

    @staticmethod
    def compile_parameter(ast, *, fun, decl, scope):
        expr = Expression.compile(ast, scope=scope)
        if expr.value_type != decl.value_type:
            raise InterfaceError(
                f"argument {decl.name} "
                f"of function {fun.name}: "
                f"expected {decl.value_type}, "
                f"got {expr.value_type}",
                parseinfo=ast.parseinfo,
            )
        return expr

    @staticmethod
    def compile(ast, scope):
        try:
            fun = scope.functions[ast.function_name]
        except KeyError:
            raise InterfaceError(
                f"function {ast.function_name} is not defined",
                parseinfo=ast.parseinfo,
            )

        if len(ast.parameters) != len(fun.signature.parameters):
            raise InterfaceError(
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
            raise InterfaceError(
                f"function {fun.name} returns {return_type}, but no return expression given",
                parseinfo=ast.parseinfo,
            )

        if return_type is None and return_value is not None:
            raise InterfaceError(
                f"function {fun.name} does not return a value",
                parseinfo=ast.return_value.parseinfo,
            )

        if return_value is not None and return_value.value_type != return_type:
            raise InterfaceError(
                f"function {fun.name} returns {return_type}, "
                f"but return expression is {return_value.value_type}",
                parseinfo=ast.return_value.parseinfo,
            )

        return CallStatement(
            function=fun,
            parameters=parameters,
            return_value=return_value,
        )

    @staticmethod
    def compile_return_value(ast, *, fun, scope):
        if ast is None:
            return_value = None
        else:
            return_value = Expression.compile(
                ast,
                scope=scope,
                expected_type=fun.signature.return_type,
            )
        return return_value

    def first_calls(self):
        return {self.function.name}

    def unroll(self, frame):
        context = FunctionCallContext(frame=frame)

        yield FunctionCallInstruction(statement=self, context=context)

        if frame.interface.signature.callbacks:
            yield from self.unroll_callbacks(frame, context)

        yield FunctionReturnInstruction(statement=self, context=context)

    def unroll_callbacks(self, frame, call_context):
        while True:
            context = AcceptCallbackContext(call=call_context)
            yield AcceptCallbackInstruction(context=context)
            if context.callback is None:
                break

            yield from context.callback.unroll(context)


class FunctionCallInstruction(Instruction):
    __slots__ = ["statement", "context"]

    def run_driver_pre(self, request):
        fun = self.statement.function
        parameters = self.statement.parameters

        if not isinstance(request, FunctionCall):
            raise InterfaceError(f"expected call to '{fun.name}', got {request}")

        if request.function_name != fun.name:
            raise InterfaceError(f"expected call to '{fun.name}', got call to '{request.function_name}'")

        for value_expr, value in zip(parameters, request.parameters):
            value_expr.evaluate_in(self.context.frame).resolve(
                value_expr.value_type.ensure(value)
            )

        self.context.accepted_callbacks = request.accepted_callbacks

    def should_send_input(self):
        has_return_type = (self.statement.function.signature.return_type is not None)
        return has_return_type


class FunctionReturnInstruction(Instruction):
    __slots__ = ["statement", "context"]

    def run_driver_post(self):
        if self.statement.function.signature.return_type:
            return_value = self.statement.return_value.evaluate_in(self.context.frame).get()
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

    def run_sandbox(self, connection):
        logger.debug("accepting callbacks...")
        connection.downward.flush()
        callback_name = read_line(connection.upward).strip()
        if callback_name == "return":
            self.context.callback = None
        else:
            interface = self.context.call.frame.interface
            self.context.callback = interface.body.scope.callbacks[callback_name]


class ReturnStatement(ImperativeStatement):
    __slots__ = ["value"]

    @staticmethod
    def compile(ast, scope):
        return ReturnStatement(
            value=Expression.compile(ast.value, scope=scope),
        )

    def unroll(self, frame):
        yield ReturnInstruction(value=self.value, frame=frame)


class ReturnInstruction(Instruction):
    __slots__ = ["value", "frame"]

    def run_driver_pre(self, request):
        assert isinstance(request, CallbackReturn)
        self.value.evaluate_in(self.frame).resolve(
            self.value.value_type.ensure(request.return_value)
        )
