import logging

from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena.driver.interface.expressions import Expression, IntLiteralSynthetic
from turingarena.driver.interface.nodes import IntermediateNode

logger = logging.getLogger(__name__)


class Print(IntermediateNode):
    __slots__ = []


class IONode(IntermediateNode, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def arguments(self):
        return [
            Expression.compile(arg)
            for arg in self.ast.arguments
        ]


class Read(IONode, IntermediateNode):
    __slots__ = []


class Write(Print, IONode):
    __slots__ = []


class Checkpoint(Print, IntermediateNode):
    __slots__ = []

    @property
    def arguments(self):
        return [IntLiteralSynthetic(0)]


class InitialCheckpoint(Checkpoint):
    def _describe_node(self):
        yield "initial checkpoint"


class CheckpointStatement(AbstractSyntaxNodeWrapper, Checkpoint):
    __slots__ = []
