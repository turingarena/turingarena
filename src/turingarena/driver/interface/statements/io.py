import logging
from collections import namedtuple

from turingarena.driver.interface.expressions import IntLiteralSynthetic
from turingarena.driver.interface.nodes import IntermediateNode

logger = logging.getLogger(__name__)


class Print(IntermediateNode):
    __slots__ = []


class IONode(IntermediateNode):
    __slots__ = []


class Read(namedtuple("Read", ["arguments"]), IONode):
    __slots__ = []


class Write(namedtuple("Write", ["arguments"]), Print, IONode):
    __slots__ = []


class Checkpoint(namedtuple("Checkpoint", []), Print, IntermediateNode):
    __slots__ = []

    @property
    def arguments(self):
        return [IntLiteralSynthetic(0)]


class InitialCheckpoint(Checkpoint):
    def _describe_node(self):
        yield "initial checkpoint"
