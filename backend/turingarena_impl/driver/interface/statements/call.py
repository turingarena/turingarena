import logging

from turingarena import InterfaceError
from turingarena_impl.driver.interface.context import StaticCallbackBlockContext
from turingarena_impl.driver.interface.diagnostics import Diagnostic
from turingarena_impl.driver.interface.execution import CallRequestSignature
from turingarena_impl.driver.interface.expressions import Expression
from turingarena_impl.driver.interface.nodes import StatementIntermediateNode, RequestLookaheadNode
from turingarena_impl.driver.interface.statements.callback import CallbackImplementation
from turingarena_impl.driver.interface.statements.statement import Statement
from turingarena_impl.driver.interface.variables import ReferenceStatus, ReferenceDirection, ReferenceAction

logger = logging.getLogger(__name__)


class CallStatement(Statement):
    __slots__ = []

    @property
    def method_name(self):
        return self.ast.name

    @property
    def method(self):
        return self.context.global_context.methods_by_name[self.method_name]

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

    def _get_has_request_lookahead(self):
        return False

    def _get_first_requests(self):
        yield CallRequestSignature("call", self.method_name)

    def _find_callback_implementation(self, index, callback):
        return next(
            CallbackImplementation(ast=implementation, context=StaticCallbackBlockContext(
                local_context=self.context,
                callback_index=index,
            ))
            for implementation in self.ast.callbacks
            if implementation.declarator.name == callback.name
        )

    def validate(self):
        if self.method_name not in self.context.global_context.methods_by_name:
            yield Diagnostic(
                Diagnostic.Messages.METHOD_NOT_DECLARED,
                self.method_name,
                parseinfo=self.ast.parseinfo,
            )
            return

        yield from self.validate_parameters()
        yield from self.validate_return_value()

    def validate_parameters(self):
        method = self.method
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

    def validate_return_value(self):
        method = self.method
        if self.return_value is not None:
            yield from self.return_value.validate()
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

    def _get_intermediate_nodes(self):
        if not self.context.has_request_lookahead:
            yield RequestLookaheadNode()

        yield MethodResolveArgumentsNode(self)

        if self.method.has_callbacks:
            yield MethodCallbacksNode(self)

        if self.method.has_return_value:
            yield MethodReturnNode(self)


class MethodResolveArgumentsNode(StatementIntermediateNode):
    __slots__ = []

    def _get_reference_actions(self):
        references = self.statement.context.get_references(ReferenceStatus.RESOLVED)
        for p in self.statement.arguments:
            if p.reference is not None and p.reference not in references:
                yield ReferenceAction(p.reference, ReferenceStatus.RESOLVED)

    def _driver_run_assignments(self, context):
        if not context.is_first_execution:
            return

        method = self.statement.method

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

        references = self.statement.context.get_references(ReferenceStatus.RESOLVED)
        for a in self.statement.arguments:
            value = context.deserialize_request_data()
            if a.reference is not None and a.reference not in references:
                logging.debug(f"Resolved parameter: {a.reference} -> {value}")
                yield a.reference, value
                # TODO: else, check value is the one expected

        has_return_value = bool(int(context.receive_driver_downward()))
        expects_return_value = (self.statement.return_value is not None)
        if not has_return_value == expects_return_value:
            names = ["procedure", "function"]
            raise InterfaceError(
                f"'{method.name}' is a {names[expects_return_value]}, "
                f"got call to {names[has_return_value]}"
            )

        callback_count = int(context.receive_driver_downward())
        expected_callback_count = len(self.statement.callbacks)
        if not callback_count == expected_callback_count:
            raise InterfaceError(
                f"'{method.name}' has a {expected_callback_count} callbacks, "
                f"got {callback_count}"
            )

        for c in self.statement.callbacks:
            parameter_count = int(context.receive_driver_downward())
            expected_parameter_count = len(c.parameters)
            if not parameter_count == expected_parameter_count:
                raise InterfaceError(
                    f"'{c.name}' has {expected_parameter_count} parameters, "
                    f"got {parameter_count}"
                )

    def _describe_node(self):
        yield f"resolve arguments ({self.statement})"


class MethodReturnNode(StatementIntermediateNode):
    __slots__ = []

    def _get_reference_actions(self):
        yield ReferenceAction(self.statement.return_value.reference, ReferenceStatus.DECLARED)

    def _get_declaration_directions(self):
        yield ReferenceDirection.UPWARD

    def _driver_run_simple(self, context):
        if context.phase is ReferenceStatus.DECLARED:
            return_value = self.statement.return_value.evaluate(context.bindings)
            context.send_driver_upward(return_value)

    def _describe_node(self):
        yield f"return ({self.statement})"


class MethodCallbacksNode(StatementIntermediateNode):
    __slots__ = []

    def _get_declaration_directions(self):
        for callback in self.statement.callbacks:
            yield from callback.body_node.declaration_directions

    def _get_reference_actions(self):
        return []

    def _can_be_grouped(self):
        return False

    def _driver_run_simple(self, context):
        while True:
            [has_callback] = context.receive_upward()
            if has_callback:
                [callback_index] = context.receive_upward()
                callback = self.statement.callbacks[callback_index]
                callback.driver_run(context)
            else:
                break
        context.send_driver_upward(0)  # no more callbacks

    def _describe_node(self):
        yield f"callbacks ({self.statement})"
        for callback in self.statement.callbacks:
            yield from self._indent_all(self._describe_callback(callback))

    def _describe_callback(self, callback):
        yield f"callback {callback.name}"
        yield from self._indent_all(callback.body_node.node_description)
