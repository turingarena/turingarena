from abc import abstractmethod

from turingarena.common import ImmutableObject
from turingarena.interface.statement import Statement


class Instruction(ImmutableObject):
    __slots__ = []

    def on_request_lookahead(self, request):
        pass

    def on_generate_response(self):
        pass

    def on_communicate_with_process(self, connection):
        pass

    def should_send_input(self):
        return False

    def is_flush(self):
        return False


class ImperativeStatement(Statement):
    __slots__ = []

    @abstractmethod
    def generate_instructions(self, frame):
        pass

    def first_calls(self):
        return {None}
