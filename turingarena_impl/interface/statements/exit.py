import logging

from turingarena import InterfaceExit
from turingarena.driver.commands import Exit
from turingarena_impl.interface.common import Instruction
from turingarena_impl.interface.statements.statement import Statement


logger = logging.getLogger(__name__)


class ExitStatement(Statement):
    __slots__ = []

    def generate_instructions(self, context):
        yield ExitInstruction()
        raise InterfaceExit

    def validate(self):
        # TODO: check that exit is used only in valid places
        return []

    def expects_request(self, request):
        return request is not None and request.request_type == "exit"


class ExitInstruction(Instruction):
    __slots__ = []

    def on_request_lookahead(self, request):
        assert isinstance(request, Exit)

    def on_generate_response(self):
        return []