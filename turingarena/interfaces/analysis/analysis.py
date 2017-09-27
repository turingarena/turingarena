from turingarena.interfaces.analysis.interface import InterfaceCompiler, compile_interface


class TaskAnalyzer:
    def analyze(self, unit):
        unit.interfaces = []
        compiler = TaskItemAnalyzer(unit)
        for item in unit.unit_items:
            item.accept(compiler)


class TaskItemAnalyzer:
    def __init__(self, task):
        self.task = task

    def visit_interface_definition(self, interface):
        compile_interface(interface)
        self.task.interfaces.append(interface)
