import logging

from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena.driver.interface.context import StaticCallbackBlockContext
from turingarena.driver.interface.diagnostics import Diagnostic
from turingarena.driver.interface.expressions import Expression, IntLiteralSynthetic
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.callback import CallbackImplementation
from turingarena.driver.interface.statements.io import Print
from turingarena.driver.interface.statements.statement import Statement
from turingarena.driver.interface.variables import ReferenceStatus, ReferenceAction

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
    def validate(self):
        if self.method_name not in self.context.global_context.methods_by_name:
            yield Diagnostic(
                Diagnostic.Messages.METHOD_NOT_DECLARED,
                self.method_name,
                parseinfo=self.ast.parseinfo,
            )
            return

        method = self.method
        if method.has_return_value and self.return_value is None:
            yield Diagnostic(
                Diagnostic.Messages.CALL_NO_RETURN_EXPRESSION, method.name,
                parseinfo=self.ast.parseinfo,
            )
        if not method.has_return_value and self.return_value is not None:
            yield Diagnostic(
                Diagnostic.Messages.METHOD_DOES_NOT_RETURN_VALUE, method.name,
                parseinfo=self.ast.return_value.parseinfo,
            )


class MethodResolveArgumentsNode(CallNode):
    __slots__ = []

    def _get_reference_actions(self):
        references = self.context.get_references(ReferenceStatus.RESOLVED)
        for p in self.arguments:
            if p.reference is not None and p.reference not in references:
                yield ReferenceAction(p.reference, ReferenceStatus.RESOLVED)

    def validate(self):
        method = self.method
        if method is None:
            return

        if len(self.arguments) != len(method.parameters):
            yield Diagnostic(
                Diagnostic.Messages.CALL_WRONG_ARGS_NUMBER,
                method.name, len(method.parameters), len(self.arguments),
                parseinfo=self.ast.parseinfo,
            )
        for parameter, expression in zip(method.parameters, self.arguments):
            yield from expression.validate()
            dimensions = self.context.dimensions(expression)
            if dimensions != parameter.dimensions:
                yield Diagnostic(
                    Diagnostic.Messages.CALL_WRONG_ARGS_TYPE,
                    parameter.name, method.name, parameter.dimensions, dimensions,
                    parseinfo=expression.ast.parseinfo,
                )

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


class MethodReturnNode(CallNode):
    __slots__ = []

    def _is_relevant(self):
        return self.return_value is not None

    def validate(self):
        method = self.method
        if method is None:
            return

        if self.return_value is not None:
            yield from self.return_value.validate()

    def _should_declare_variables(self):
        return True

    def _get_reference_actions(self):
        yield ReferenceAction(self.return_value.reference, ReferenceStatus.DECLARED)

    def _describe_node(self):
        yield f"return"


class MethodCallCompletedNode(CallNode):
    def _describe_node(self):
        yield f"call completed"


class PrintNoCallbacks(CallNode, Print):
    def _is_relevant(self):
        return self.method and self.method.callbacks

    @property
    def arguments(self):
        return [IntLiteralSynthetic(0)]

    def _get_comment(self):
        return "no more callbacks"


class MethodCallbacksNode(CallNode):
    __slots__ = []

    def _is_relevant(self):
        return self.method and self.method.has_callbacks

    def _describe_node(self):
        yield f"callbacks"
        for callback in self.callbacks:
            yield from self._indent_all(self._describe_callback(callback))

    def _describe_callback(self, callback):
        yield f"callback {callback.name}"
        yield from self._indent_all(callback.body.node_description)
