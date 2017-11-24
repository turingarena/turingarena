import logging

from collections import OrderedDict

from turingarena.common import ImmutableObject, TupleLikeObject
from turingarena.protocol.model.node import AbstractSyntaxNode
from turingarena.protocol.model.scope import Scope
from turingarena.protocol.model.type_expressions import ValueType
from turingarena.protocol.server.commands import CallbackCall
from turingarena.protocol.server.data import VariableReference
from turingarena.protocol.server.frames import Phase

logger = logging.getLogger(__name__)


class Main(ImmutableObject):
    __slots__ = ["body"]


class Protocol(AbstractSyntaxNode):
    __slots__ = ["id", "body"]

    @staticmethod
    def compile(*, ast, **kwargs):
        logger.debug("compiling {}".format(ast))
        scope = Scope()
        return Protocol(
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
        if context.phase is Phase.PREFLIGHT:
            request = context.engine.peek_request()
            assert request.message_type == "main_begin"
            for variable, value in zip(self.signature.variables.values(), request.global_variables):
                context.engine.root_frame[variable] = value
            context.engine.complete_request()

        yield from run_body(main.body, context=context)

        if context.phase is Phase.PREFLIGHT:
            request = context.engine.peek_request()
            assert request.message_type == "main_end"
            context.engine.complete_request()

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

        return CallableSignature(
            name=ast.name,
            parameters=parameters,
            return_type=ValueType.compile(ast.return_type, scope=scope),
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

            yield from run_body(self.body, context=inner_context)

            if context.phase is Phase.PREFLIGHT:
                request = context.engine.peek_request()
                assert request.message_type == "callback_return"
                # TODO: handle return value
                context.engine.complete_request()


# FIXME: here to avoid circular import, find better solution
from turingarena.protocol.model.statements import run_body, Body
