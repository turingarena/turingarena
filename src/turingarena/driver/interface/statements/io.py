import logging
from abc import abstractmethod

from turingarena.driver.client.exceptions import InterfaceError
from turingarena.driver.interface.exceptions import CommunicationError
from turingarena.driver.interface.expressions import Expression
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.phase import ExecutionPhase
from turingarena.driver.interface.statements.statement import Statement
from turingarena.driver.interface.variables import ReferenceStatus, ReferenceDirection, ReferenceAction

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
        if context.phase is ExecutionPhase.DOWNWARD:
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

    def _get_assignments(self, context):
        values = context.receive_upward()
        for a, value in zip(self.arguments, values):
            yield a.reference, value

    def _driver_run(self, context):
        if context.phase is ExecutionPhase.UPWARD:
            return context.result()._replace(assignments=list(self._get_assignments(context)))


class CheckpointStatement(Statement, IntermediateNode):
    __slots__ = []

    def _get_intermediate_nodes(self):
        yield CheckpointNode()


class CheckpointNode(IntermediateNode):
    def _get_declaration_directions(self):
        yield ReferenceDirection.UPWARD

    def _get_reference_actions(self):
        return []

    def _needs_request_lookahead(self):
        return True

    def _driver_run(self, context):
        if context.phase is ExecutionPhase.UPWARD:
            values = context.receive_upward()
            if values != (0,):
                raise CommunicationError(f"expecting checkpoint, got {values}")
        if context.phase is ExecutionPhase.REQUEST:
            command = context.request_lookahead.command
            if not command == "checkpoint":
                raise InterfaceError(f"expecting 'checkpoint', got '{command}'")
            context.report_ready()
            return context.result().with_request_processed()
