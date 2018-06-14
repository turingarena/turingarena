from collections import namedtuple

from turingarena import InterfaceError
from turingarena_impl.interface.block import Block, BlockNode
from turingarena_impl.interface.callables import CallbackPrototype
from turingarena_impl.interface.expressions import Expression, SyntheticExpression
from turingarena_impl.interface.nodes import IntermediateNode, StatementIntermediateNode
from turingarena_impl.interface.statements.statement import Statement, SyntheticStatement
from turingarena_impl.interface.variables import ReferenceAction, ReferenceStatus, Reference, ReferenceDirection


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

    def _get_declaration_directions(self):
        return self.body_node.declaration_directions


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


class CallbackCallNode(StatementIntermediateNode):
    def _get_reference_actions(self):
        for p in self.statement.parameters:
            yield ReferenceAction(reference=p.reference, status=ReferenceStatus.DECLARED)

    def _get_declaration_directions(self):
        yield ReferenceDirection.UPWARD

    def _driver_run(self, context):
        if context.phase is ReferenceStatus.DECLARED:
            for p in self.statement.parameters:
                r = Reference(p, index_count=0)
                value = context.bindings[r]
                context.send_driver_upward(value)


class ReturnStatement(Statement, IntermediateNode):
    __slots__ = []

    @property
    def value(self):
        return Expression.compile(self.ast.value, self.context)

    def _get_intermediate_nodes(self):
        yield self

    def validate(self):
        yield from self.value.validate()

    def _get_reference_actions(self):
        yield ReferenceAction(reference=self.value.reference, status=ReferenceStatus.RESOLVED)

    def _driver_run(self, context):
        if context.phase is ReferenceStatus.RESOLVED:
            command = context.receive_driver_downward()
            if not command == "callback_return":
                raise InterfaceError(f"expecting 'callback_return', got '{command}'")
            has_return_value = int(context.receive_driver_downward())
            if not has_return_value:
                raise InterfaceError(
                    f"callback '{self.context.callback}' is a function, "
                    f"but the provided implementation did not return anything"
                )
            value = int(context.receive_driver_downward())

            yield self.value.reference, value


class ExitStatement(Statement, IntermediateNode):
    __slots__ = []

    def _get_intermediate_nodes(self):
        yield self

    def validate(self):
        # TODO: check that exit is used only in valid places
        return []

    def expects_request(self, request):
        return request is not None and request.request_type == "exit"

    def _get_reference_actions(self):
        return []

    def _driver_run(self, context):
        # TODO
        pass
