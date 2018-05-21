import logging
from collections import namedtuple

from turingarena_impl.interface.common import Instruction
from turingarena_impl.interface.expressions import Expression
from turingarena_impl.interface.statements.statement import Statement

logger = logging.getLogger(__name__)


class CheckpointStatement(Statement):
    __slots__ = []

    def generate_instructions(self, bindings):
        yield CheckpointInstruction()


class CheckpointInstruction(Instruction):
    __slots__ = []

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


class ReadWriteInstruction(Instruction, namedtuple("ReadWriteInstruction", [
    "arguments", "bindings"
])):
    __slots__ = []


class ReadStatement(ReadWriteStatement):
    __slots__ = []

    def generate_instructions(self, bindings):
        yield ReadInstruction(arguments=self.arguments, bindings=bindings)

    def _get_declared_references(self):
        for exp in self.arguments:
            yield exp.reference

    @property
    def needs_flush(self):
        return True


class ReadInstruction(ReadWriteInstruction):
    __slots__ = []

    def has_downward(self):
        return True

    def on_communicate_downward(self, lines):
        lines.send([
            a.evaluate(self.bindings)
            for a in self.arguments
        ])


class WriteStatement(ReadWriteStatement):
    __slots__ = []

    def generate_instructions(self, bindings):
        yield WriteInstruction(arguments=self.arguments, bindings=bindings)


class WriteInstruction(ReadWriteInstruction):
    __slots__ = []

    def has_upward(self):
        return True

    def on_communicate_upward(self, lines):
        for a, value in zip(self.arguments, next(lines)):
            pass
            # a.assign(self.bindings, value)
