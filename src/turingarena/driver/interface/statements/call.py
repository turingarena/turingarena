import logging
from collections.__init__ import namedtuple

from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena.driver.interface.expressions import Expression, IntLiteralSynthetic
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.callback import CallbackImplementation
from turingarena.driver.interface.statements.io import Print
from turingarena.driver.interface.statements.statement import Statement
from turingarena.driver.interface.variables import ReferenceStatus

logger = logging.getLogger(__name__)


class CallNode(IntermediateNode, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def method_name(self):
        return self.ast.name

    @property
    def method(self):
        return self.context.global_context.methods_by_name.get(self.method_name)

    @property
    def arguments(self):
        return [
            Expression.compile(p, self.context.expression())
            for p in self.ast.arguments
        ]

    @property
    def return_value(self):
        if self.ast.return_value:
            return Expression.compile(self.ast.return_value, self.context.expression(
                reference=True,
                declaring=True,
            ))
        else:
            return None

    @property
    def callbacks(self):
        return [
            self._find_callback_implementation(i, s)
            for i, s in enumerate(self.method.callbacks)
        ]

    def _find_callback_implementation(self, index, callback):
        try:
            return next(
                CallbackImplementation(ast=implementation, context=StaticCallbackBlockContext(
                    local_context=self.context,
                    callback_index=index,
                ), description=None)
                for implementation in self.ast.callbacks
                if implementation.declarator.name == callback.name
            )
        except StopIteration:
            return CallbackImplementation(ast=callback.ast, context=StaticCallbackBlockContext(
                local_context=self.context,
                callback_index=index,
            ), description=None)


class Call(Statement, CallNode):
    pass


class CallArgumentsResolve(CallNode):
    __slots__ = []

    def _get_assignments(self, context):
        references = self.context.get_references(ReferenceStatus.RESOLVED)
        for a in self.arguments:
            value = context.deserialize_request_data()
            if a.reference is not None and a.reference not in references:
                logging.debug(f"Resolved parameter: {a.reference} -> {value}")
                yield a.reference, value
                # TODO: else, check value is the one expected

    def _describe_node(self):
        yield f"resolve arguments"


class CallReturn(CallNode):
    __slots__ = []

    def _describe_node(self):
        yield f"return"


class CallCompleted(CallNode):
    def _describe_node(self):
        yield f"call completed"


class PrintNoCallbacks(CallNode, Print):
    @property
    def arguments(self):
        return [IntLiteralSynthetic(0)]


class AcceptCallbacks(CallNode):
    __slots__ = []

    def _describe_node(self):
        yield f"callbacks"
        for callback in self.callbacks:
            yield from self._indent_all(self._describe_callback(callback))

    def _describe_callback(self, callback):
        yield f"callback {callback.name}"
        yield from self._indent_all(callback.body.node_description)


class StaticCallbackBlockContext(namedtuple("StaticCallbackBlockContext", [
    "local_context",
    "callback_index",
])):
    pass