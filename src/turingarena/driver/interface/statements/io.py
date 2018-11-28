import logging
from collections import namedtuple

from turingarena.driver.interface.expressions import Expression, IntLiteralSynthetic
from turingarena.driver.interface.nodes import IntermediateNode

logger = logging.getLogger(__name__)


class Print(IntermediateNode):
    __slots__ = []


class IONode(IntermediateNode):
    __slots__ = []

    @property
    def arguments(self):
        return [
            Expression.compile(arg)
            for arg in self.ast.arguments
        ]


class Read(namedtuple("Read", ["ast"]), IONode):
    __slots__ = []


class Write(namedtuple("Write", ["ast"]), Print, IONode):
    __slots__ = []


class Checkpoint(Print, IntermediateNode):
    __slots__ = []

    @property
    def arguments(self):
        return [IntLiteralSynthetic(0)]


class InitialCheckpoint(Checkpoint):
    def _describe_node(self):
        yield "initial checkpoint"


class CheckpointStatement(namedtuple("CheckpointStatement", ["ast"]), Checkpoint):
    __slots__ = []
