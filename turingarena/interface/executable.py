from abc import abstractmethod
from typing import Iterator

from turingarena.common import ImmutableObject
from turingarena.interface.frames import Frame
from turingarena.interface.statement import Statement


class Instruction(ImmutableObject):
    __slots__ = []

    def run_driver_pre(self, request):
        pass

    def run_sandbox(self, connection):
        pass

    def run_driver_post(self):
        pass

    def should_send_input(self):
        return False

    def is_flush(self):
        return False


class ExecutableStructure(ImmutableObject):
    __slots__ = []

    @abstractmethod
    def unroll(self, frame: Frame) -> Iterator[Instruction]:
        pass

    def first_calls(self):
        return {None}


class ImperativeStatement(Statement, ExecutableStructure):
    __slots__ = []


class SimpleStatement(ImperativeStatement):
    __slots__ = []

    def unroll(self, frame):
        yield StatementInstruction(statement=self, frame=frame)

    def run_driver_pre(self, request, *, frame):
        pass

    def run_sandbox(self, connection, *, frame):
        pass

    def run_driver_post(self, *, frame):
        pass

    def should_send_input(self, *, frame):
        return False

    def is_flush(self, *, frame):
        return False


class StatementInstruction(Instruction):
    __slots__ = ["statement", "frame"]


instruction_methods = [
    "run_driver_pre",
    "run_sandbox",
    "run_driver_post",
    "should_send_input",
    "is_flush",
]


def make_method(method_name):
    def method(self, *args, **kwargs):
        statement_method = getattr(self.statement, method_name)
        return statement_method(*args, **kwargs, frame=self.frame)

    return method


for method_name in instruction_methods:
    setattr(StatementInstruction, method_name, make_method(method_name))
