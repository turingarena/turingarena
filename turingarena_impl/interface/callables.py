import logging
from collections import namedtuple

from turingarena import InterfaceError
from turingarena_impl.interface.block import Block, BlockNode
from turingarena_impl.interface.common import AbstractSyntaxNodeWrapper
from turingarena_impl.interface.diagnostics import Diagnostic
from turingarena_impl.interface.expressions import SyntheticExpression
from turingarena_impl.interface.nodes import IntermediateNode, StatementIntermediateNode
from turingarena_impl.interface.statements.statement import SyntheticStatement
from turingarena_impl.interface.variables import Variable, Reference, ReferenceAction, ReferenceStatus, \
    ReferenceDirection

logger = logging.getLogger(__name__)


class ParameterDeclaration(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def variable(self):
        return Variable(
            name=self.ast.name,
            dimensions=len(self.ast.indexes),
        )


class CallablePrototype(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def name(self):
        return self.ast.declarator.name

    @property
    def parameter_declarations(self):
        return [
            ParameterDeclaration(ast=p, context=self.context)
            for p in self.ast.declarator.parameters
        ]

    @property
    def parameters(self):
        return [
            p.variable
            for p in self.parameter_declarations
        ]

    @property
    def has_return_value(self):
        return self.ast.declarator.type == 'function'

    @property
    def callbacks(self):
        return [
            CallbackPrototype(callback, self.context)
            for callback in self.ast.callbacks
        ]

    @property
    def has_callbacks(self):
        return bool(self.callbacks)

    def validate(self):
        return []


class MethodPrototype(CallablePrototype):
    __slots__ = []


class CallbackPrototype(CallablePrototype):
    __slots__ = []

    def validate(self):
        for callback in self.callbacks:
            yield Diagnostic(
                Diagnostic.Messages.UNEXPECTED_CALLBACK,
                callback.name,
                parseinfo=callback.ast.parseinfo,
            )
        for parameter in self.parameter_declarations:
            if parameter.variable.value_type.dimensions:
                yield Diagnostic(
                    Diagnostic.Messages.CALLBACK_PARAMETERS_MUST_BE_SCALARS,
                    parseinfo=parameter.ast.parseinfo,
                )


class SyntheticCallbackBody(namedtuple("SyntheticCallbackBody", ["context", "body"])):
    @property
    def synthetic_statements(self):
        callback_index = self.context.callback_index
        yield SyntheticStatement("write", arguments=[
            SyntheticExpression("int_literal", value=1),  # more callbacks
        ])
        yield SyntheticStatement("write", arguments=[
            SyntheticExpression("int_literal", value=callback_index),
        ])
        yield from self.body.synthetic_statements


class CallbackImplementation(IntermediateNode, CallbackPrototype):
    __slots__ = []

    @property
    def synthetic_body(self):
        return SyntheticCallbackBody(
            self.context,
            self.body,
        )

    @property
    def body(self):
        # TODO: generate block if body is None ('default' is specified)
        inner_context = self.context.local_context.with_reference_actions(
            ReferenceAction(reference=Reference(variable=p, index_count=0), status=ReferenceStatus.DECLARED)
            for p in self.parameters
        )
        return Block(
            ast=self.ast.body,
            context=inner_context,
        )

    def validate(self):
        yield from self.prototype.validate()

    def _generate_inner_nodes(self):
        yield CallbackCallNode(self)
        yield from self.body.flat_inner_nodes

    @property
    def body_node(self):
        return BlockNode.from_nodes(self._generate_inner_nodes())

    def _driver_run(self, context):
        context.send_driver_upward(1)
        context.send_driver_upward(self.context.callback_index)
        self.body_node.driver_run(context)

        # FIXME: some redundancy with ReturnStatement
        if not self.has_return_value:
            command = context.receive_driver_downward()
            if not command == "callback_return":
                raise InterfaceError(f"expecting 'callback_return', got '{command}'")

            has_return_value = bool(int(context.receive_driver_downward()))
            if has_return_value:
                raise InterfaceError(
                    f"callback '{self.context.callback}' is a procedure, "
                    f"but the provided implementation returned something"
                )

    def _get_directions(self):
        return self.body_node.directions


class CallbackCallNode(StatementIntermediateNode):
    def _get_reference_actions(self):
        for p in self.statement.parameters:
            yield ReferenceAction(reference=p.reference, status=ReferenceStatus.DECLARED)

    def _get_directions(self):
        yield ReferenceStatus.DECLARED, ReferenceDirection.UPWARD

    def _driver_run(self, context):
        if context.phase is ReferenceStatus.DECLARED:
            for p in self.statement.parameters:
                r = Reference(p, index_count=0)
                value = context.bindings[r]
                context.send_driver_upward(value)
