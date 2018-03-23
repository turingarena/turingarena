import logging

from turingarena.common import TupleLikeObject, ImmutableObject
from turingarena.interface.body import Body
from turingarena.interface.context import CallbackContext
from turingarena.interface.exceptions import InterfaceError
from turingarena.interface.executable import Instruction
from turingarena.interface.references import VariableReference
from turingarena.interface.statement import Statement
from turingarena.interface.type_expressions import ValueType, ScalarType
from turingarena.interface.variables import Variable

logger = logging.getLogger(__name__)


class CallableSignature(TupleLikeObject):
    __slots__ = ["name", "parameters", "return_type"]

    @staticmethod
    def compile(ast):
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
    def compile(ast):
        return Function(
            name=ast.declarator.name,
            signature=CallableSignature.compile(ast.declarator),
        )


class FunctionStatement(Statement):
    __slots__ = []

    @property
    def function(self):
        return Function.compile(self.ast)


class Callback(Callable):
    __slots__ = ["body"]

    @staticmethod
    def compile(ast):
        signature = CallableSignature.compile(ast.declarator)

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

        return Callback(
            name=ast.declarator.name,
            signature=signature,
            body=Body.compile(ast.body)
        )

    def generate_instructions(self, context):
        global_context = context.call_context.local_context.procedure.global_context
        callback_context = CallbackContext(accept_context=context, global_context=global_context)

        local_context = callback_context.child({p.name: p for p in self.signature.parameters})
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
    __slots__ = []

    @property
    def callback(self):
        return Callback.compile(self.ast)
