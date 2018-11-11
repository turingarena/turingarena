import logging

from turingarena.driver.client.exceptions import InterfaceError
from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena.driver.interface.context import StaticCallbackBlockContext
from turingarena.driver.interface.diagnostics import Diagnostic
from turingarena.driver.interface.execution import CallRequestSignature
from turingarena.driver.interface.expressions import Expression, SyntheticExpression
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.phase import ExecutionPhase
from turingarena.driver.interface.statements.callback import CallbackImplementation
from turingarena.driver.interface.statements.statement import Statement, AbstractStatement
from turingarena.driver.interface.variables import ReferenceStatus, ReferenceDirection, ReferenceAction

logger = logging.getLogger(__name__)


class CallStatementNode(IntermediateNode, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def method_name(self):
        return self.ast.name

    @property
    def method(self):
        try:
            return self.context.global_context.methods_by_name[self.method_name]
        except KeyError:
            return None

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

    def _get_first_requests(self):
        yield CallRequestSignature("call", self.method_name)

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


class CallStatement(Statement, CallStatementNode):
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

    def _driver_run(self, context):
        pass


class MethodResolveArgumentsNode(CallStatementNode):
    __slots__ = []

    def _needs_request_lookahead(self):
        return True

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
            if expression.dimensions != parameter.dimensions:
                yield Diagnostic(
                    Diagnostic.Messages.CALL_WRONG_ARGS_TYPE,
                    parameter.name, method.name, parameter.dimensions, expression.dimensions,
                    parseinfo=expression.ast.parseinfo,
                )

    def _driver_run(self, context):
        if context.phase is not ExecutionPhase.REQUEST:
            return

        method = self.method

        command = context.request_lookahead.command
        if not command == "call":
            raise InterfaceError(f"expected call to '{method.name}', got {command}")

        method_name = context.request_lookahead.method_name
        if not method_name == method.name:
            raise InterfaceError(f"expected call to '{method.name}', got call to '{method_name}'")

        parameter_count = int(context.receive_driver_downward())
        if parameter_count != len(method.parameters):
            raise InterfaceError(
                f"'{method.name}' expects {len(method.parameters)} arguments, "
                f"got {parameter_count}"
            )

        assignments = list(self._get_assignments(context))

        has_return_value = bool(int(context.receive_driver_downward()))
        expects_return_value = (self.return_value is not None)
        if not has_return_value == expects_return_value:
            names = ["procedure", "function"]
            raise InterfaceError(
                f"'{method.name}' is a {names[expects_return_value]}, "
                f"got call to {names[has_return_value]}"
            )

        callback_count = int(context.receive_driver_downward())
        expected_callback_count = len(self.callbacks)
        if not callback_count == expected_callback_count:
            raise InterfaceError(
                f"'{method.name}' has a {expected_callback_count} callbacks, "
                f"got {callback_count}"
            )

        for c in self.callbacks:
            parameter_count = int(context.receive_driver_downward())
            expected_parameter_count = len(c.parameters)
            if not parameter_count == expected_parameter_count:
                raise InterfaceError(
                    f"'{c.name}' has {expected_parameter_count} parameters, "
                    f"got {parameter_count}"
                )

        return context.result().with_request_processed()._replace(
            assignments=assignments,
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


class MethodReturnNode(CallStatementNode):
    __slots__ = []

    def _is_relevant(self):
        return self.return_value is not None

    def validate(self):
        method = self.method
        if method is None:
            return

        if self.return_value is not None:
            yield from self.return_value.validate()

    def _get_reference_actions(self):
        yield ReferenceAction(self.return_value.reference, ReferenceStatus.DECLARED)

    def _get_declaration_directions(self):
        yield ReferenceDirection.UPWARD

    def _driver_run(self, context):
        if context.phase is ExecutionPhase.REQUEST:
            return_value = self.return_value.evaluate(context.bindings)
            context.report_ready()
            context.send_driver_upward(return_value)

    def _describe_node(self):
        yield f"return"


class MethodCallCompletedNode(CallStatementNode):
    def _driver_run(self, context):
        if context.phase is ExecutionPhase.REQUEST:
            context.report_ready()
            context.send_driver_upward(0)  # no more callbacks

    def _describe_node(self):
        yield f"call completed"


class MethodCallbacksStopNode(CallStatementNode, AbstractStatement):
    def _driver_run(self, context):
        pass

    def _is_relevant(self):
        return self.method and self.method.callbacks

    def _get_comment(self):
        return "no more callbacks"

    @property
    def statement_type(self):
        return "write"

    @property
    def arguments(self):
        return [SyntheticExpression("int_literal", value=0)]


class MethodCallbacksNode(CallStatementNode):
    __slots__ = []

    def _is_relevant(self):
        return self.method and self.method.has_callbacks

    def _get_declaration_directions(self):
        for callback in self.callbacks:
            yield from callback.body.declaration_directions

    def _can_be_grouped(self):
        return False

    def _driver_run(self, context):
        while True:
            [has_callback] = context.receive_upward()
            if has_callback:
                [callback_index] = context.receive_upward()
                callback = self.callbacks[callback_index]
                callback.driver_run(context)
            else:
                break

    def _describe_node(self):
        yield f"callbacks"
        for callback in self.callbacks:
            yield from self._indent_all(self._describe_callback(callback))

    def _describe_callback(self, callback):
        yield f"callback {callback.name}"
        yield from self._indent_all(callback.body.node_description)
