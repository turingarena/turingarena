from turingarena.interfaces.analysis.statement import accept_statement

from turingarena.interfaces.analysis.interface import InterfaceCompiler, compile_interface


class TaskAnalyzer:
    def analyze(self, unit):
        unit.interfaces = []
        compiler = TaskItemAnalyzer(unit)
        for statement in unit.statements:
            accept_statement(statement, visitor=compiler)


class TaskItemAnalyzer:
    def __init__(self, unit):
        self.unit = unit

    def visit_interface_statement(self, statement):
        compile_interface(statement)
        self.unit.interfaces.append(statement)
