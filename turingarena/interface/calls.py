import logging

from turingarena.interface.exceptions import InterfaceError
from turingarena.interface.executable import SimpleStatement, ImperativeStatement, Instruction
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
    def compile(ast, scope):
        fun = scope.functions[ast.function_name]
        assert len(ast.parameters) == len(fun.signature.parameters)
        if ast.return_value is None:
            return_value = None
        else:
            return_value = Expression.compile(
                ast.return_value,
                scope=scope,
                expected_type=fun.signature.return_type,
            )
        return CallStatement(
            function=fun,
            parameters=[
                Expression.compile(arg, scope=scope, expected_type=decl_arg.value_type)
                for decl_arg, arg in zip(fun.signature.parameters, ast.parameters)
            ],
            return_value=return_value,
        )

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

        if request.request_type != "function_call":
            raise InterfaceError(f"expected call to '{fun.name}', got {request.request_type}")

        if request.function_name != fun.name:
            raise InterfaceError(f"expected call to '{fun.name}', got call to '{request.function_name}'")

        for value_expr, value in zip(parameters, request.parameters):
            value_expr.evaluate_in(self.context.frame).resolve(value)

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


class ReturnStatement(SimpleStatement):
    __slots__ = ["value"]

    @staticmethod
    def compile(ast, scope):
        return ReturnStatement(
            value=Expression.compile(ast.value, scope=scope),
        )

    def run_driver_pre(self, request, *, frame):
        assert request.request_type == "callback_return"
        self.value.evaluate_in(frame).resolve(request.return_value)
