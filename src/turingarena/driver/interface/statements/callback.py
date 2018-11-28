import functools
import logging
from collections import namedtuple

from turingarena.driver.interface.block import Block, AbstractContextBlock
from turingarena.driver.interface.expressions import IntLiteralSynthetic
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.io import Print

logger = logging.getLogger(__name__)


class PrintCallbackRequest(Print, namedtuple("PrintCallbackRequest", ["context"])):
    @property
    def arguments(self):
        return [IntLiteralSynthetic(value=1)]


class PrintCallbackIndex(namedtuple("CallbackWriteIndexNode", ["implementation", "context"]), Print):
    @property
    def callback_index(self):
        return self.implementation.context.callback_index

    @property
    def arguments(self):
        return [IntLiteralSynthetic(value=self.callback_index)]


class CallbackBody(AbstractContextBlock):
    def __init__(self, ast, context, implementation):
        self.ast = ast
        self.context = context
        self.implementation = implementation

    def _get_flat_children_builders(self):
        yield functools.partial(CallbackStart, self.implementation)
        yield PrintCallbackRequest
        yield functools.partial(PrintCallbackIndex, self.implementation)

        yield from Block(self.ast, self.context)._get_flat_children_builders()

        if not self.implementation.prototype.has_return_value:
            yield functools.partial(CallbackEnd, self.implementation)


class CallbackImplementation(namedtuple("CallbackImplementation", ["ast", "context", "prototype"])):
    __slots__ = []

    @property
    def body(self):
        return CallbackBody(
            ast=self.ast.body if self.ast.body else self.default_body,
            context=self.context.local_context,
            implementation=self,
        )

    @property
    def default_body(self):
        fake_ast_body = [
            namedtuple("write", ["statement_type", "arguments"])("write", [
                namedtuple("expression", ["expression_type", "variable_name", "indices"])("reference_subscript", p.name,
                                                                                          "")
                for p in self.prototype.parameters
            ])
        ]
        if self.prototype.has_return_value:
            return_var = namedtuple("expression", ["expression_type", "variable_name", "indices"])(
                "reference_subscript", "_result", "")
            fake_ast_body += [
                namedtuple("read", ["statement_type", "arguments"])("read", [return_var]),
                namedtuple("ret", ["statement_type", "value"])("return", return_var),
            ]
        return namedtuple("body", ["statements"])(fake_ast_body)


class CallbackStart(IntermediateNode, namedtuple("CallbackStart", [
    "callback_implementation",
    "context",
])):
    def _describe_node(self):
        yield "callback_call"


class Return(namedtuple("Return", ["value"]), IntermediateNode):
    __slots__ = []

    def _describe_node(self):
        yield f"callback return"


class CallbackEnd(IntermediateNode, namedtuple("CallbackEnd", ["callback", "context"])):
    def _describe_node(self):
        yield f"callback end"


class Exit(namedtuple("Exit", []), IntermediateNode):
    __slots__ = []
