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
