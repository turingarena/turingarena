import logging
from collections import namedtuple

from turingarena.interface.exceptions import CommunicationBroken, Diagnostic
from turingarena.interface.executable import Instruction, ImperativeStatement
from turingarena.interface.expressions import compile_expression

logger = logging.getLogger(__name__)


def read_line(pipe):
    line = pipe.readline()
    if not line:
        raise CommunicationBroken
    return line


class CheckpointStatement(ImperativeStatement):
    __slots__ = []

    def generate_instructions(self, context):
        yield CheckpointInstruction()

    @property
    def context_after(self):
        return self.context.with_flushed_output(False)


class CheckpointInstruction(Instruction):
    __slots__ = []

    def should_send_input(self):
        return True

    def on_communicate_with_process(self, connection):
        # make sure all input was sent before receiving output
        connection.downward.flush()

        line = read_line(connection.upward).strip()
        assert line == str(0)


class InputOutputStatement(ImperativeStatement):
    __slots__ = []

    @property
    def arguments(self):
        return [
            compile_expression(arg, self.context)
            for arg in self.ast.arguments
        ]

    def validate(self):
        for exp in self.arguments:
            yield from exp.validate()


class InputOutputInstruction(Instruction, namedtuple("InputInstruction", [
    "arguments", "context"
])):
    __slots__ = []


class InputStatement(InputOutputStatement):
    __slots__ = []

    def generate_instructions(self, context):
        yield InputInstruction(arguments=self.arguments, context=context)

    @property
    def context_after(self):
        return self.context.with_initialized_variables({
            exp.resolve_variable()
            for exp in self.arguments
        })

    def validate(self):
        if not self.context.has_flushed_output:
            yield Diagnostic("missing flush between output and input instructions", parseinfo=self.ast.parseinfo)
        for exp in self.arguments:
            yield from exp.validate(lvalue=True)


class InputInstruction(InputOutputInstruction):
    __slots__ = []

    def on_communicate_with_process(self, connection):
        raw_values = [
            a.evaluate_in(self.context).get()
            for a in self.arguments
        ]
        try:
            print(*raw_values, file=connection.downward)
        except BrokenPipeError:
            raise CommunicationBroken


class OutputStatement(InputOutputStatement):
    __slots__ = []

    def generate_instructions(self, context):
        yield OutputInstruction(arguments=self.arguments, context=context)

    @property
    def context_after(self):
        return self.context.with_flushed_output(False)


class OutputInstruction(InputOutputInstruction):
    __slots__ = []

    def on_communicate_with_process(self, connection):
        # make sure all input was sent before receiving output
        connection.downward.flush()

        raw_values = read_line(connection.upward).strip().split()
        for a, v in zip(self.arguments, raw_values):
            value = int(v)
            a.evaluate_in(self.context).resolve(value)


class FlushStatement(ImperativeStatement):
    __slots__ = []

    def generate_instructions(self, context):
        yield FlushInstruction()

    @property
    def context_after(self):
        return self.context.with_flushed_output(True)


class FlushInstruction(Instruction):
    __slots__ = []

    def is_flush(self):
        return True
