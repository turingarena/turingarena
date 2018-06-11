import logging

from turingarena_impl.interface.nodes import IntermediateNode
from turingarena_impl.interface.statements.statement import Statement

logger = logging.getLogger(__name__)


class ExitStatement(Statement, IntermediateNode):
    __slots__ = []

    def _get_intermediate_nodes(self):
        yield self

    def validate(self):
        # TODO: check that exit is used only in valid places
        return []

    def expects_request(self, request):
        return request is not None and request.request_type == "exit"

    def _get_reference_actions(self):
        return []

    def _get_direction(self):
        return None

    def _driver_run(self, context):
        # TODO
        pass
