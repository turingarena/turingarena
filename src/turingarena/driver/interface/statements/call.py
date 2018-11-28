import logging
from collections.__init__ import namedtuple

from turingarena.driver.interface.expressions import IntLiteral
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.io import Print

logger = logging.getLogger(__name__)


class CallNode(namedtuple("CallNode", [
    "method",
    "arguments",
    "return_value",
    "callbacks",
]), IntermediateNode):
    __slots__ = []


class Call(CallNode):
    __slots__ = []


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


class PrintNoCallbacks(CallNode):
    __slots__ = []


class AcceptCallbacks(CallNode):
    __slots__ = []

    def _describe_node(self):
        yield f"callbacks"
        for callback in self.callbacks:
            yield from self._indent_all(self._describe_callback(callback))

    def _describe_callback(self, callback):
        yield f"callback {callback.prototype.name}"
        yield from self._indent_all(callback.body.node_description)
