import logging
from abc import abstractmethod

from turingarena.driver.client.exceptions import InterfaceError
from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena.driver.interface.exceptions import CommunicationError
from turingarena.driver.interface.expressions import Expression, IntLiteralSynthetic
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.phase import ExecutionPhase
from turingarena.driver.interface.variables import ReferenceStatus, ReferenceDirection, ReferenceAction

logger = logging.getLogger(__name__)


class Print(IntermediateNode):
    __slots__ = []


class ReadWriteStatement(IntermediateNode, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def arguments(self):
        return [
            Expression.compile(arg, self._get_arguments_context())
            for arg in self.ast.arguments
        ]

    def validate(self):
        for exp in self.arguments:
            yield from exp.validate()

    @abstractmethod
    def _get_arguments_context(self):
        pass

    def _should_declare_variables(self):
        return True


class Read(ReadWriteStatement, IntermediateNode):
    __slots__ = []

    def _get_arguments_context(self):
        return self.context.expression(
            reference=True,
            declaring=True,
        )

    def _get_intermediate_nodes(self):
        yield self

    def _get_reference_actions(self):
        for exp in self.arguments:
            yield ReferenceAction(exp.reference, ReferenceStatus.DECLARED)

    def _get_declaration_directions(self):
        yield ReferenceDirection.DOWNWARD


class Write(Print, ReadWriteStatement):
    __slots__ = []

    def _get_arguments_context(self):
        return self.context.expression(
            reference=True,
        )

    def _get_intermediate_nodes(self):
        yield self

    def _get_reference_actions(self):
        for exp in self.arguments:
            yield ReferenceAction(exp.reference, ReferenceStatus.RESOLVED)


class Checkpoint(Print, IntermediateNode):
    __slots__ = []

    def _get_declaration_directions(self):
        yield ReferenceDirection.UPWARD

    def _get_reference_actions(self):
        return []

    @property
    def arguments(self):
        return [IntLiteralSynthetic(0)]


class InitialCheckpoint(Checkpoint):
    def _get_comment(self):
        return "initial checkpoint"

    def _describe_node(self):
        yield "initial checkpoint"


class CheckpointStatement(AbstractSyntaxNodeWrapper, Checkpoint):
    __slots__ = []
