import logging
from collections import namedtuple

from turingarena.driver.interface.nodes import IntermediateNode

logger = logging.getLogger(__name__)


class Print(namedtuple("Print", ["arguments"])):
    __slots__ = []


class IONode(IntermediateNode):
    __slots__ = []


class Read(namedtuple("Read", ["arguments"]), IONode):
    __slots__ = []


class Write(namedtuple("Write", ["arguments"]), IONode):
    __slots__ = []


class Checkpoint(namedtuple("Checkpoint", []), IntermediateNode):
    __slots__ = []


class InitialCheckpoint(Checkpoint):
    def _describe_node(self):
        yield "initial checkpoint"
