import logging
from collections import namedtuple

from turingarena.driver.interface.block import Block, AbstractBlock
from turingarena.driver.interface.callables import CallbackPrototype
from turingarena.driver.interface.requests import RequestSignature
from turingarena.driver.interface.expressions import Expression, IntLiteralSynthetic
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.io import Print
from turingarena.driver.interface.statements.statement import Statement
from turingarena.driver.interface.variables import ReferenceAction, ReferenceStatus, ReferenceDirection

logger = logging.getLogger(__name__)


class PrintCallbackRequest(Print):
    @property
    def arguments(self):
        return [IntLiteralSynthetic(value=1)]

    def _get_comment(self):
        return "requesting a callback"


class PrintCallbackIndex(namedtuple("CallbackWriteIndexNode", ["implementation"]), Print):
    @property
    def callback_index(self):
        return self.implementation.context.callback_index

    @property
    def arguments(self):
        return [IntLiteralSynthetic(value=self.callback_index)]

    def _get_comment(self):
        return f"index of this callback: {self.callback_index} = {self.implementation.name}"


class CallbackBody(AbstractBlock):
    def __init__(self, implementation):
        self.implementation = implementation

    def _generate_flat_inner_nodes(self):
        yield CallbackCallNode(self.implementation)
        yield PrintCallbackRequest()
        yield PrintCallbackIndex(self.implementation)

        yield from self.implementation.raw_body.flat_inner_nodes

        if not self.implementation.has_return_value:
            yield CallbackEnd(callback=self.implementation)


class CallbackImplementation(IntermediateNode, CallbackPrototype):
    __slots__ = []

    @property
    def raw_body(self):
        inner_context = self.context.local_context.with_reference_actions(
            ReferenceAction(reference=p.as_reference(), status=ReferenceStatus.DECLARED)
            for p in self.parameters
        )
        return Block(
            ast=self.ast.body if self.ast.body else self.default_body,
            context=inner_context,
        )

    @property
    def body(self):
        return CallbackBody(self)

    @property
    def default_body(self):
        fake_ast_body = [
            namedtuple("write", ["statement_type", "arguments"])("write", [
                namedtuple("expression", ["expression_type", "variable_name", "indices"])("reference_subscript", p.name,
                                                                                          "")
                for p in self.parameters
            ])
        ]
        if self.has_return_value:
            return_var = namedtuple("expression", ["expression_type", "variable_name", "indices"])(
                "reference_subscript", "_result", "")
            fake_ast_body += [
                namedtuple("read", ["statement_type", "arguments"])("read", [return_var]),
                namedtuple("ret", ["statement_type", "value"])("return", return_var),
            ]
        return namedtuple("body", ["statements"])(fake_ast_body)

    def validate(self):
        yield from self.prototype.validate()

    def _get_declaration_directions(self):
        return self.body.declaration_directions


class CallbackCallNode(IntermediateNode, namedtuple("CallbackCallNode", [
    "callback_implementation",
])):
    def _get_reference_actions(self):
        for p in self.callback_implementation.parameters:
            yield ReferenceAction(reference=p.as_reference(), status=ReferenceStatus.DECLARED)

    def _get_declaration_directions(self):
        yield ReferenceDirection.UPWARD

    def _describe_node(self):
        yield "callback_call"


class Return(IntermediateNode, Statement):
    __slots__ = []

    @property
    def value(self):
        return Expression.compile(self.ast.value, self.context.expression(reference=True))

    def validate(self):
        yield from self.value.validate()

    def _get_reference_actions(self):
        yield ReferenceAction(reference=self.value.reference, status=ReferenceStatus.RESOLVED)

    def _describe_node(self):
        yield f"callback return"


class CallbackEnd(IntermediateNode, namedtuple("CallbackEnd", ["callback"])):
    def _describe_node(self):
        yield f"callback end"


class Exit(IntermediateNode):
    __slots__ = []


class ExitStatement(Exit, Statement, IntermediateNode):
    __slots__ = []

    def _get_intermediate_nodes(self):
        yield self

    def validate(self):
        # TODO: check that exit is used only in valid places
        return []

    def _get_first_requests(self):
        yield RequestSignature("exit")

    def _get_reference_actions(self):
        return []

    @property
    def does_break(self):
        return True
