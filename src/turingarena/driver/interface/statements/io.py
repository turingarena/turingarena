import logging
from abc import abstractmethod

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
            Expression.compile(arg, self._get_arguments_context())
            for arg in self.ast.arguments
        ]

    @abstractmethod
    def _get_arguments_context(self):
        pass


class Read(IONode, IntermediateNode):
    __slots__ = []

    def _get_arguments_context(self):
        return self.context.expression(
            reference=True,
            declaring=True,
        )


class Write(Print, IONode):
    __slots__ = []

    def _get_arguments_context(self):
        return self.context.expression(
            reference=True,
        )


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
