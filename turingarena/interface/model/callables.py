import logging

from turingarena.common import TupleLikeObject, ImmutableObject
from turingarena.interface.driver.frames import Phase
from turingarena.interface.driver.references import VariableReference
from turingarena.interface.exceptions import InterfaceError
from turingarena.interface.model.body import Body
from turingarena.interface.model.scope import Scope
from turingarena.interface.model.statement import Statement
from turingarena.interface.model.type_expressions import ValueType, ScalarType
from turingarena.interface.model.variables import Variable

logger = logging.getLogger(__name__)


class Main(ImmutableObject):
    __slots__ = ["body"]


class MainStatement(Statement):
    __slots__ = ["main"]

    @staticmethod
    def compile(ast, scope):
        main = Main(body=Body.compile(ast.body, scope=scope))
        scope.main["main"] = main
        return MainStatement(main=main)


class CallableSignature(TupleLikeObject):
    __slots__ = ["name", "parameters", "return_type"]

    @staticmethod
    def compile(ast, scope):
        parameters = [
            Variable(
                value_type=ValueType.compile(p.type.expression, scope=scope),
                name=p.declarator.name,
            )
            for p in ast.parameters
        ]

        if ast.return_type is None:
            return_type = None
        else:
            return_type = ValueType.compile(ast.return_type.expression, scope=scope)
            if not isinstance(return_type, ScalarType):
                raise InterfaceError(
                    "return type must be a scalar",
                    parseinfo=ast.return_type.parseinfo,
                )

        return CallableSignature(
            name=ast.name,
            parameters=parameters,
            return_type=return_type
        )


class Callable(ImmutableObject):
    __slots__ = ["name", "signature"]


class Function(Callable):
    __slots__ = []

    @staticmethod
    def compile(ast, scope):
        return Function(
            name=ast.declarator.name,
            signature=CallableSignature.compile(ast.declarator, scope),
        )


class FunctionStatement(Statement):
    __slots__ = ["function"]

    @staticmethod
    def compile(ast, scope):
        fun = Function.compile(ast, scope)
        scope.functions[fun.name] = fun
        return FunctionStatement(
            function=fun
        )


class Callback(Callable):
    __slots__ = ["scope", "body"]

    @staticmethod
    def compile(ast, scope):
        signature = CallableSignature.compile(ast.declarator, scope)

        invalid_parameter = next(
            (
                a for p, a in zip(signature.parameters, ast.declarator.parameters)
                if not isinstance(p.value_type, ScalarType)
            ),
            None
        )

        if invalid_parameter is not None:
            raise InterfaceError(
                "callback arguments must be scalars",
                parseinfo=invalid_parameter.parseinfo,
            )

        callback_scope = Scope(scope)
        for p in signature.parameters:
            callback_scope.variables[p.name] = p
        return Callback(
            name=ast.declarator.name,
            signature=signature,
            scope=callback_scope,
            body=Body.compile(ast.body, scope=callback_scope)
        )

    def run(self, context):
        logger.debug(f"running callback {self.name}")

        with context.enter(self.scope) as inner_context:
            if context.phase is Phase.PREFLIGHT:
                parameters = [
                    VariableReference(frame=inner_context.frame, variable=p).get()
                    for p in self.signature.parameters
                ]

                with context.engine.response() as p:
                    for v in parameters:
                        assert isinstance(v, int)
                        p(v)

            yield from self.body.run(inner_context)

            if context.phase is Phase.PREFLIGHT:
                context.engine.process_request(expected_type="callback_return")


class CallbackStatement(Statement):
    __slots__ = ["callback"]

    @staticmethod
    def compile(ast, scope):
        callback = Callback.compile(ast, scope=scope)
        scope.callbacks[callback.name] = callback
        return CallbackStatement(callback=callback)
