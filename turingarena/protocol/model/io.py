import logging
from abc import abstractmethod

from turingarena.protocol.driver.frames import Phase
from turingarena.protocol.exceptions import CommunicationBroken
from turingarena.protocol.model.expressions import Expression
from turingarena.protocol.model.statement import ImperativeStatement

logger = logging.getLogger(__name__)


class InputOutputStatement(ImperativeStatement):
    __slots__ = ["arguments"]

    @classmethod
    def compile(cls, ast, scope):
        return cls(
            arguments=[
                Expression.compile(arg, scope=scope)
                for arg in ast.arguments
            ],
        )

    def run(self, context):
        if context.phase is Phase.RUN:
            self.on_run(context)
        yield from []

    @abstractmethod
    def on_run(self, context):
        pass


class InputStatement(InputOutputStatement):
    __slots__ = []

    def on_run(self, context):
        raw_values = [
            a.value_type.format(a.evaluate(frame=context.frame).get())
            for a in self.arguments
        ]
        logger.debug(f"printing {raw_values} to downward_pipe")
        # FIXME: should flush only once per communication block
        try:
            print(*raw_values, file=context.engine.sandbox_connection.downward, flush=True)
        except BrokenPipeError:
            raise CommunicationBroken


class OutputStatement(InputOutputStatement):
    __slots__ = []

    def on_run(self, context):
        logger.debug(f"reading from upward_pipe...")
        line = context.engine.sandbox_connection.upward.readline()
        if not line:
            raise CommunicationBroken
        raw_values = line.strip().split()
        logger.debug(f"read values {raw_values} from upward_pipe")
        for a, v in zip(self.arguments, raw_values):
            value = a.value_type.parse(v)
            context.evaluate(a).resolve(value)


class FlushStatement(ImperativeStatement):
    __slots__ = []

    @staticmethod
    def compile(ast, scope):
        return FlushStatement()

    def run(self, context):
        if context.phase is Phase.RUN:
            yield
        else:
            context.engine.flush()
