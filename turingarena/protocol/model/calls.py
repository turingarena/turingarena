import logging

from turingarena.protocol.driver.frames import RootBlockContext, Phase
from turingarena.protocol.exceptions import ProtocolError
from turingarena.protocol.model.expressions import Expression
from turingarena.protocol.model.statement import ImperativeStatement

logger = logging.getLogger(__name__)


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

    def preflight(self, context):
        request = context.engine.process_request(expected_type="function_call")

        if request.function_name != self.function.name:
            raise ProtocolError(f"expected call to '{self.function.name}', got '{request.function_name}'")

        for value_expr, value in zip(self.parameters, request.parameters):
            context.evaluate(value_expr).resolve(value)

        return_type = self.function.signature.return_type
        if return_type or request.accepted_callbacks:
            context.engine.ensure_output()

        while True:
            if not context.engine.interface.signature.callbacks:
                logger.debug(f"no callback defined, nothing to do")
                break

            logger.debug(f"popping callbacks")
            callback_context = context.engine.pop_callback()
            if callback_context is None:
                logger.debug(f"popped None")
                break
            logger.debug(f"popped callback")
            with context.engine.response() as p:
                p(1)  # has callbacks
                p(request.accepted_callbacks.index(callback_context.callback.name))
            yield from callback_context.callback.run(context.engine.new_context(
                root_block_context=callback_context,
                phase=context.phase,
            ))
            context.engine.ensure_output()

        with context.engine.response() as p:
            p(0)  # no more callbacks

        with context.engine.response() as p:
            if return_type:
                return_value = context.evaluate(self.return_value).get()
                p(1)  # has return value
                p(return_value)
            else:
                p(0)  # no return value

    def accept_callbacks(self, context):
        if not context.engine.interface.signature.callbacks:
            return
        while True:
            logger.debug("accepting callbacks...")
            callback_name = context.engine.sandbox_connection.upward.readline().strip()
            if callback_name == "return":
                logger.debug(f"no more callbacks, push None to callback queue")
                context.engine.push_callback(None)
                break
            else:
                callback = context.engine.interface.body.scope.callbacks[callback_name]
                callback_context = RootBlockContext(callback)
                context.engine.push_callback(callback_context)
                logger.debug(f"got callback '{callback_name}', pushing to queue")
                yield from callback.run(context=context.engine.new_context(
                    root_block_context=callback_context,
                    phase=context.phase,
                ))

    def run(self, context):
        if context.phase is Phase.RUN:
            yield from self.accept_callbacks(context)
        if context.phase is Phase.PREFLIGHT:
            yield from self.preflight(context)

    def first_calls(self):
        return {self.function.name}


class ReturnStatement(ImperativeStatement):
    __slots__ = ["value"]

    @staticmethod
    def compile(ast, scope):
        return ReturnStatement(
            value=Expression.compile(ast.value, scope=scope),
        )

    def run(self, context):
        if context.phase is Phase.PREFLIGHT:
            request = context.engine.peek_request(expected_type="callback_return")
            context.evaluate(self.value).resolve(request.return_value)
        yield from []
