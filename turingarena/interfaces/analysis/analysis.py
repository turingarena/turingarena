import logging

from turingarena.interfaces.analysis.interface import compile_interface
from turingarena.interfaces.visitor import accept_statement

logger = logging.getLogger(__name__)


class TaskAnalyzer:
    def analyze(self, unit):
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
