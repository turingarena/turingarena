import logging

from turingarena.protocol.analysis.interface import compile_interface
from turingarena.protocol.visitor import accept_statement

logger = logging.getLogger(__name__)


def analyze_protocol(unit):
    logger.debug("compiling {}".format(unit))
    unit.interfaces = []
    compiler = TaskItemAnalyzer(unit)
    for statement in unit.statements:
        accept_statement(statement, visitor=compiler)


class TaskItemAnalyzer:
    def __init__(self, unit):
        self.unit = unit

    def visit_interface_statement(self, statement):
        logger.debug("compiling interface {}".format(statement))
        compile_interface(statement)
        self.unit.interfaces.append(statement)
