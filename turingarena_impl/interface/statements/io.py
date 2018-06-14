import logging
from abc import abstractmethod

from turingarena_impl.interface.context import ExpressionContext
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
        context = ExpressionContext.in_statement(self.context, declaring=self._is_declaring())
        return [
            Expression.compile(arg, context)
            for arg in self.ast.arguments
        ]

    def validate(self):
        for exp in self.arguments:
            yield from exp.validate_reference()

    @abstractmethod
    def _is_declaring(self):
        pass


class ReadStatement(ReadWriteStatement, IntermediateNode):
    __slots__ = []

    def _is_declaring(self):
        return True

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

    def _is_declaring(self):
        return False

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
        # TODO: in the declare phase, process the checkpoint request
        if context.phase is ReferenceStatus.RESOLVED:
            values = context.receive_upward()
            if values != (0,):
                raise CommunicationBroken(f"expecting checkpoint, got {values}")
