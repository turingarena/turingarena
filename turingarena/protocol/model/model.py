import logging
from collections import OrderedDict

from turingarena.common import ImmutableObject, TupleLikeObject
from turingarena.protocol.exceptions import ProtocolError, ProtocolExit
from turingarena.protocol.model.node import AbstractSyntaxNode
from turingarena.protocol.model.scope import Scope
from turingarena.protocol.model.type_expressions import ValueType, ScalarType
from turingarena.protocol.driver.commands import CallbackCall
from turingarena.protocol.driver.frames import Phase
from turingarena.protocol.driver.references import VariableReference

logger = logging.getLogger(__name__)


class Main(ImmutableObject):
    __slots__ = ["body"]


class ProtocolDefinition(AbstractSyntaxNode):
    __slots__ = ["body"]

    @staticmethod
    def compile(*, ast, **kwargs):
        logger.debug("compiling {}".format(ast))
        scope = Scope()
        return ProtocolDefinition(
            body=Body.compile(ast.body, scope=scope),
            **kwargs,
        )


class Variable(ImmutableObject):
    __slots__ = ["value_type", "name"]


class InterfaceSignature(TupleLikeObject):
    __slots__ = ["variables", "functions", "callbacks"]


class Interface(ImmutableObject):
    __slots__ = ["name", "signature", "body"]

    @staticmethod
    def compile(ast, scope):
        body = Body.compile(ast.body, scope=scope)
        signature = InterfaceSignature(
            variables=OrderedDict(body.scope.variables.items()),
            functions={
                c.name: c.signature
                for c in body.scope.functions.values()
            },
            callbacks={
                c.name: c.signature
                for c in body.scope.callbacks.values()
            },
        )
        return Interface(
            name=ast.name,
            signature=signature,
            body=body,
        )

    def run(self, context):
        main = self.body.scope.main["main"]

        logger.debug(f"running main {main} in {context}")

        if context.phase is Phase.PREFLIGHT:
            request = context.engine.process_request(expected_type="main_begin")
            for variable, value in zip(self.signature.variables.values(), request.global_variables):
                context.engine.root_frame[variable] = value

        try:
            yield from main.body.run(context)
        except ProtocolExit:
            logger.debug(f"exit was reached in {context}")
            if context.phase is Phase.PREFLIGHT:
                context.engine.process_request(expected_type="exit")
        else:
            logger.debug(f"main body reached end in {context}")
            if context.phase is Phase.PREFLIGHT:
                context.engine.process_request(expected_type="main_end")

        if context.phase is Phase.RUN:
            # end of last communication block
            yield


class CallableSignature(TupleLikeObject):
    __slots__ = ["name", "parameters", "return_type"]

    @staticmethod
    def compile(ast, scope):
        parameters = [
            Variable(
                value_type=ValueType.compile(p.type_expression, scope=scope),
                name=p.declarator.name,
            )
            for p in ast.parameters
        ]

        if ast.return_type is None:
            return_type = None
        else:
            return_type = ValueType.compile(ast.return_type, scope=scope)
            if not isinstance(return_type, ScalarType):
                raise ProtocolError(
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
            raise ProtocolError(
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
        logger.debug(f"running callback {self.name} in {context}")

        with context.enter(self.scope) as inner_context:
            if context.phase is Phase.PREFLIGHT:
                response = CallbackCall(
                    interface_signature=context.engine.interface.signature,
                    callback_name=self.name,
                    parameters=[
                        VariableReference(frame=inner_context.frame, variable=p).get()
                        for p in self.signature.parameters
                    ],
                )
                context.engine.send_response(response)

            yield from self.body.run(inner_context)

            if context.phase is Phase.PREFLIGHT:
                context.engine.process_request(expected_type="callback_return")


# FIXME: here to avoid circular import, find better solution
from turingarena.protocol.model.statements import Body
