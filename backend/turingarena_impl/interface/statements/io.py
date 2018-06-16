import logging
from abc import abstractmethod

from turingarena import InterfaceError
from turingarena_impl.interface.exceptions import CommunicationBroken
from turingarena_impl.interface.expressions import Expression
from turingarena_impl.interface.nodes import IntermediateNode
from turingarena_impl.interface.statements.statement import Statement
from turingarena_impl.interface.variables import ReferenceStatus, ReferenceDirection, ReferenceAction

logger = logging.getLogger(__name__)


class ReadWriteStatement(Statement):
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


class ReadStatement(ReadWriteStatement, IntermediateNode):
    __slots__ = []

    def _get_arguments_context(self):
        return self.context.expression(
            reference=True,
            declaring=True,
        )

    def _get_intermediate_nodes(self):
        yield self

    @property
    def needs_flush(self):
        return True

    def _get_reference_actions(self):
        for exp in self.arguments:
            yield ReferenceAction(exp.reference, ReferenceStatus.DECLARED)

    def _get_declaration_directions(self):
        yield ReferenceDirection.DOWNWARD

    def _driver_run(self, context):
        if context.phase is ReferenceStatus.DECLARED:
            logging.debug(f"Bindings: {context.bindings}")
            context.send_downward([
                a.evaluate(context.bindings)
                for a in self.arguments
            ])


class WriteStatement(ReadWriteStatement, IntermediateNode):
    __slots__ = []

    def _get_arguments_context(self):
        return self.context.expression(
            reference=True,
            declaring=False,
        )

    def _get_intermediate_nodes(self):
        yield self

    def _get_reference_actions(self):
        for exp in self.arguments:
            yield ReferenceAction(exp.reference, ReferenceStatus.RESOLVED)

    def _driver_run(self, context):
        if context.phase is ReferenceStatus.RESOLVED:
            values = context.receive_upward()
            for a, value in zip(self.arguments, values):
                yield a.reference, value


class CheckpointStatement(Statement, IntermediateNode):
    __slots__ = []

    def _get_intermediate_nodes(self):
        yield self

    def _get_declaration_directions(self):
        yield ReferenceDirection.UPWARD

    def _get_reference_actions(self):
        return []

    def _driver_run(self, context):
        if context.phase is ReferenceStatus.DECLARED:
            command = context.receive_driver_downward()
            if not command == "checkpoint":
                raise InterfaceError(f"expecting 'checkpoint', got '{command}'")
            context.send_driver_upward(0)
        if context.phase is ReferenceStatus.RESOLVED:
            values = context.receive_upward()
            if values != (0,):
                raise CommunicationBroken(f"expecting checkpoint, got {values}")
