from abc import abstractmethod
from typing import Iterable, Tuple, Any

from turingarena.driver.commands import DriverMessage
from turingarena_impl.interface.variables import Reference

CommunicationLines = Iterable[Tuple[int, ...]]
Assignments = Iterable[Tuple[Reference, Any]]


class Instruction:
    __slots__ = []

    def generate_response(self) -> Iterable[DriverMessage]:
        pass

    def communicate_upward(self, lines: CommunicationLines) -> Assignments:
        pass

    def lookahead_request(self, request: DriverMessage) -> Assignments:
        pass

    def should_advance_request(self) -> bool:
        pass

    def communicate_downward(self) -> CommunicationLines:
        pass


class InstructionExecutor:
    @abstractmethod
    def execute(self, instruction: Instruction) -> Assignments:
        pass
