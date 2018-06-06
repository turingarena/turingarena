import logging

from turingarena_impl.interface.expressions import Expression
from turingarena_impl.interface.nodes import IntermediateNode
from turingarena_impl.interface.statements.statement import Statement
from turingarena_impl.interface.variables import ReferenceStatus, ReferenceDirection, ReferenceAction

logger = logging.getLogger(__name__)


class CheckpointStatement(Statement, IntermediateNode):
    __slots__ = []

    def _get_intermediate_nodes(self):
        yield self

    def _get_direction(self):
        return ReferenceDirection.UPWARD

    def _get_reference_actions(self):
        return []

    def should_send_input(self):
        return True

    def has_upward(self):
        return True

    def on_communicate_upward(self, lines):
        assert next(lines) == (0,)


class ReadWriteStatement(Statement):
    __slots__ = []

    @property
    def arguments(self):
        return [
            Expression.compile(arg, self.context)
            for arg in self.ast.arguments
        ]

    def validate(self):
        for exp in self.arguments:
            yield from exp.validate_reference()


class ReadStatement(ReadWriteStatement, IntermediateNode):
    __slots__ = []

    def _get_intermediate_nodes(self):
        yield self

    @property
    def needs_flush(self):
        return True

    def _get_reference_actions(self):
        for exp in self.arguments:
            yield ReferenceAction(exp.reference, ReferenceStatus.DECLARED)

    def _get_direction(self):
        return ReferenceDirection.DOWNWARD

    def on_communicate_downward(self, lines):
        lines.send([
            a.evaluate(self.bindings)
            for a in self.arguments
        ])


class WriteStatement(ReadWriteStatement, IntermediateNode):
    __slots__ = []

    def _get_intermediate_nodes(self):
        yield self

    def _get_reference_actions(self):
        for exp in self.arguments:
            yield ReferenceAction(exp.reference, ReferenceStatus.RESOLVED)

    def _get_direction(self):
        return ReferenceDirection.UPWARD

    def has_upward(self):
        return True

    def on_communicate_upward(self, lines):
        for a, value in zip(self.arguments, next(lines)):
            pass
            # a.assign(self.bindings, value)
