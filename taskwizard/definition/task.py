from taskwizard.definition.module import ModuleDefinition
from taskwizard.definition.interface import InterfaceDefinition
from taskwizard.definition.protocol import ProtocolStatementDefinition
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
        self.interfaces = ast.get("interface_definitions", [])
        self.modules = ast.get("module_definitions", [])
