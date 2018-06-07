from typing import Iterable, Tuple, Any, List

from turingarena.driver.commands import DriverMessage
from turingarena_impl.interface.variables import Reference

CommunicationLines = Iterable[Tuple[int, ...]]
Assignments = List[Tuple[Reference, Any]]


class UpwardDeclareInstruction:
    __slots__ = []

    def generate_response(self) -> Iterable[DriverMessage]:
        raise NotImplementedError


class UpwardResolveInstruction:
    def communicate_upward(self, lines: CommunicationLines) -> Assignments:
        raise NotImplementedError


class DownwardResolveInstruction:
    def lookahead_request(self, request: DriverMessage) -> Assignments:
        raise NotImplementedError

    def should_advance_request(self) -> bool:
        raise NotImplementedError


class DownwardDeclareInstruction:
    def communicate_downward(self) -> CommunicationLines:
        raise NotImplementedError
