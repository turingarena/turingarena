import logging

from turingarena.interface.exceptions import CommunicationBroken
from turingarena.interface.executable import SimpleStatement
from turingarena.interface.expressions import Expression

logger = logging.getLogger(__name__)


def read_line(pipe):
    line = pipe.readline()
    if not line:
        raise CommunicationBroken
    return line


class CheckpointStatement(SimpleStatement):
    __slots__ = []

    @staticmethod
    def compile(ast, scope):
        return CheckpointStatement()

    def should_send_input(self, *, frame):
        return True

    def run_sandbox(self, connection, *, frame):
        # make sure all input was sent before receiving output
        connection.downward.flush()

        logger.debug(f"reading from upward pipe...")
        line = read_line(connection.upward).strip()
        assert line == str(0)


class InputOutputStatement(SimpleStatement):
    __slots__ = ["arguments"]

    @classmethod
    def compile(cls, ast, scope):
        return cls(
            arguments=[
                Expression.compile(arg, scope=scope)
                for arg in ast.arguments
            ],
        )


class InputStatement(InputOutputStatement):
    __slots__ = []

    def run_sandbox(self, connection, *, frame):
        raw_values = [
            a.value_type.format(a.evaluate_in(frame).get())
            for a in self.arguments
        ]
        logger.debug(f"printing {raw_values} to downward pipe")
        try:
            print(*raw_values, file=connection.downward)
        except BrokenPipeError:
            raise CommunicationBroken


class OutputStatement(InputOutputStatement):
    __slots__ = []

    def run_sandbox(self, connection, *, frame):
        # make sure all input was sent before receiving output
        connection.downward.flush()

        raw_values = read_line(connection.upward).strip().split()
        logger.debug(f"read values {raw_values} from upward_pipe")
        for a, v in zip(self.arguments, raw_values):
            value = a.value_type.parse(v)
            a.evaluate_in(frame).resolve(value)


class FlushStatement(SimpleStatement):
    __slots__ = []

    @staticmethod
    def compile(ast, scope):
        return FlushStatement()

    def is_flush(self, *, frame):
        return True
