import logging

from turingarena.common import TupleLikeObject, ImmutableObject
from turingarena.interface.body import Body
from turingarena.interface.context import CallbackContext
from turingarena.interface.exceptions import InterfaceError
from turingarena.interface.executable import Instruction
from turingarena.interface.references import VariableReference
from turingarena.interface.scope import Scope
from turingarena.interface.statement import Statement
from turingarena.interface.type_expressions import ValueType, ScalarType
from turingarena.interface.variables import Variable

logger = logging.getLogger(__name__)


class CallableSignature(TupleLikeObject):
    __slots__ = ["name", "parameters", "return_type"]

    @staticmethod
    def compile(ast, scope):
        parameters = [
            Variable(
                value_type=ValueType.compile(p.type.expression),
                name=p.declarator.name,
            )
            for p in ast.parameters
        ]

        if ast.return_type is None:
            return_type = None
        else:
            return_type = ValueType.compile(ast.return_type.expression)
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
            ast=ast,
            function=fun,
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

    def generate_instructions(self, context):
        global_context = context.call_context.local_context.procedure.global_context
        callback_context = CallbackContext(accept_context=context, global_context=global_context)

        local_context = callback_context.child(self.scope)
        yield CallbackCallInstruction(
            callback_context=callback_context,
            local_context=local_context,
        )
        yield from self.body.generate_instructions(local_context)


class CallbackCallInstruction(Instruction):
    __slots__ = ["callback_context", "local_context"]

    @property
    def callback(self):
        return self.callback_context.accept_context.callback

    def on_generate_response(self):
        parameters = [
            VariableReference(
                context=self.local_context,
                variable=p,
                value_type=p.value_type,
            ).get()
            for p in self.callback.signature.parameters
        ]

        assert all(isinstance(v, int) for v in parameters)
        accepted_callbacks = list(self.callback_context.accept_context.call_context.accepted_callbacks.keys())
        return (
            [1] +  # has callback
            [accepted_callbacks.index(self.callback.name)] +
            parameters
        )


class CallbackStatement(Statement):
    __slots__ = ["callback"]

    @staticmethod
    def compile(ast, scope):
        callback = Callback.compile(ast, scope=scope)
        scope.callbacks[callback.name] = callback
        return CallbackStatement(ast=ast, callback=callback)
