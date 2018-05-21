import logging

from turingarena import InterfaceExit
from turingarena.driver.commands import Exit
from turingarena_impl.interface.common import StatementInstruction
from turingarena_impl.interface.statements.statement import Statement

logger = logging.getLogger(__name__)


class ExitStatement(Statement):
    __slots__ = []

    def _get_instructions(self):
        yield ExitInstruction(self)

    def generate_instructions(self, bindings):
        yield ExitInstruction()
        raise InterfaceExit

    def validate(self):
        # TODO: check that exit is used only in valid places
        return []

    @property
    def may_process_requests(self):
        return True

    def expects_request(self, request):
        return request is not None and request.request_type == "exit"


class ExitInstruction(StatementInstruction):
    __slots__ = []

    def on_request_lookahead(self, request):
        assert isinstance(request, Exit)

    def on_generate_response(self):
        return []
