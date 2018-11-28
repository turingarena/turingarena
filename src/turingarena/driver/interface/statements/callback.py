import logging
from collections import namedtuple

from turingarena.driver.interface.nodes import IntermediateNode

logger = logging.getLogger(__name__)


class PrintCallbackRequest(namedtuple("PrintCallbackRequest", []), IntermediateNode):
    __slots__ = []


class PrintCallbackIndex(namedtuple("PrintCallbackIndex", ["index", "prototype"]), IntermediateNode):
    __slots__ = []


class CallbackImplementation(namedtuple("CallbackImplementation", [
    "index",
    "prototype",
    "body",
])):
    __slots__ = []

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


class CallbackStart(namedtuple("CallbackStart", [
    "prototype",
]), IntermediateNode):
    def _describe_node(self):
        yield "callback_call"


class Return(namedtuple("Return", ["value"]), IntermediateNode):
    __slots__ = []

    def _describe_node(self):
        yield f"callback return"


class CallbackEnd(namedtuple("CallbackEnd", []), IntermediateNode):
    def _describe_node(self):
        yield f"callback end"


class Exit(namedtuple("Exit", []), IntermediateNode):
    __slots__ = []
