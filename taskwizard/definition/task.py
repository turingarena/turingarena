from collections import OrderedDict

from taskwizard.definition.declarations import named_definitions
from taskwizard.definition.module import ModuleDefinition
from taskwizard.definition.interface import Interface, InterfaceDefinition
from taskwizard.definition.syntax import AbstractSyntaxNode


class TaskDefinition(AbstractSyntaxNode):

    grammar_production = "task_definition"
    grammar = """
        task_definition =
        {
        | module_definitions+:module_definition
        | interface_definitions+:interface_definition
        }* $ ;
    """
    grammar_deps = lambda: [ModuleDefinition, InterfaceDefinition]

    def __init__(self, ast):
        self.name = ast.name
        self.interface_definitions = ast.get("interface_definitions", [])
        self.module_definitions = ast.get("module_definitions", [])


class Task:

    def __init__(self, definition):
        self.definition = definition
        #self.modules = named_definitions(definition.modules)
        self.interfaces = OrderedDict(
                (d.name, Interface(d))
                for d in definition.interface_definitions
        )
