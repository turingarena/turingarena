from taskwizard.compile.interface import InterfaceCompiler


class TaskCompiler:

    def compile(self, task):
        task.interfaces = []
        compiler = TaskItemCompiler(task)
        for item in task.task_items:
            item.accept(compiler)


class TaskItemCompiler:

    def __init__(self, task):
        self.task = task

    def visit_interface_definition(self, interface):
        InterfaceCompiler().compile(interface)
        self.task.interfaces.append(interface)