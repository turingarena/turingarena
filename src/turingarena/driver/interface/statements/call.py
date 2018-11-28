import logging
from collections.__init__ import namedtuple

from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena.driver.interface.expressions import Expression, IntLiteralSynthetic
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.callback import CallbackImplementation
from turingarena.driver.interface.statements.io import Print
from turingarena.driver.interface.statements.statement import Statement

logger = logging.getLogger(__name__)


class CallNode(AbstractSyntaxNodeWrapper, IntermediateNode):
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
            Expression.compile(p)
            for p in self.ast.arguments
        ]

    @property
    def return_value(self):
        if self.ast.return_value:
            return Expression.compile(self.ast.return_value)
        else:
            return None

    @property
    def callbacks(self):
        return [
            self._find_callback_implementation(i, s)
            for i, s in enumerate(self.method.callbacks)
        ]

    def _find_callback_implementation(self, index, callback):
        asts = [
            ast
            for ast in self.ast.callbacks
            if ast.declarator.name == callback.name
        ]
        if asts:
            [ast] = asts
        else:
            ast = None

        return CallbackImplementation(
            ast=ast,
            prototype=callback,
            context=StaticCallbackBlockContext(
                local_context=self.context,
                callback_index=index,
            ),
        )


class Call(Statement, CallNode):
    pass


class CallArgumentsResolve(CallNode):
    __slots__ = []

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
        yield f"callback {callback.prototype.name}"
        yield from self._indent_all(callback.body.node_description)


class StaticCallbackBlockContext(namedtuple("StaticCallbackBlockContext", [
    "local_context",
    "callback_index",
])):
    pass
