import logging

from turingarena.interface.exceptions import CommunicationBroken
from turingarena.interface.executable import Instruction, ImperativeStatement
from turingarena.interface.expressions import Expression

logger = logging.getLogger(__name__)


def read_line(pipe):
    line = pipe.readline()
    if not line:
        raise CommunicationBroken
    return line


class CheckpointStatement(ImperativeStatement):
    __slots__ = []

    @staticmethod
    def compile(ast, scope):
        return CheckpointStatement(ast=ast)

    def generate_instructions(self, context):
        yield CheckpointInstruction()


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
    __slots__ = ["arguments"]

    @classmethod
    def compile(cls, ast, scope):
        return cls(
            ast=ast,
            arguments=[
                Expression.compile(arg, scope=scope)
                for arg in ast.arguments
            ],
        )

    def check_variables(self, initialized_variables, allocated_variables):
        for exp in self.arguments:
            exp.check_variables(initialized_variables, allocated_variables)

class InputStatement(InputOutputStatement):
    __slots__ = []

    def generate_instructions(self, context):
        yield InputInstruction(arguments=self.arguments, context=context)

    def initialized_variables(self):
        return [
            exp.resolve_variable()
            for exp in self.arguments
        ]


class InputInstruction(Instruction):
    __slots__ = ["arguments", "context"]

    def on_communicate_with_process(self, connection):
        raw_values = [
            a.value_type.format(a.evaluate_in(self.context).get())
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



class OutputInstruction(Instruction):
    __slots__ = ["arguments", "context"]

    def on_communicate_with_process(self, connection):
        # make sure all input was sent before receiving output
        connection.downward.flush()

        raw_values = read_line(connection.upward).strip().split()
        for a, v in zip(self.arguments, raw_values):
            value = a.value_type.parse(v)
            a.evaluate_in(self.context).resolve(value)


class FlushStatement(ImperativeStatement):
    __slots__ = []

    @staticmethod
    def compile(ast, scope):
        return FlushStatement(ast=ast)

    def generate_instructions(self, context):
        yield FlushInstruction()


class FlushInstruction(Instruction):
    __slots__ = []

    def is_flush(self):
        return True
