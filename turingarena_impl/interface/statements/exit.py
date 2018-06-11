import logging

from turingarena import InterfaceExit
from turingarena_impl.interface.nodes import StatementIntermediateNode
from turingarena_impl.interface.statements.statement import Statement

logger = logging.getLogger(__name__)


class ExitStatement(Statement):
    __slots__ = []

    def _get_intermediate_nodes(self):
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


class ExitInstruction(StatementIntermediateNode):
    __slots__ = []

    def on_request_lookahead(self, request):
        assert isinstance(request, Exit)

    def on_generate_response(self):
        return []
