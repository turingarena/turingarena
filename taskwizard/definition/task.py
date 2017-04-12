from collections import OrderedDict

from taskwizard.definition.declarations import named_definitions
from taskwizard.definition.driver import DriverDefinition
from taskwizard.definition.interface import Interface, InterfaceDefinition
from taskwizard.definition.syntax import AbstractSyntaxNode
from taskwizard.definition.test_case import TestCaseDefinition


class TaskDefinition(AbstractSyntaxNode):

    grammar_production = "task_definition"
    grammar = """
        task_definition =
        {
        | interface_definitions+:interface_definition
        | driver_definitions+:driver_definition
        | test_case_definitions+:test_case_definition
        }* $ ;
    """
    grammar_deps = lambda: [InterfaceDefinition, DriverDefinition, TestCaseDefinition]

    def __init__(self, ast):
        self.name = ast.name
        self.interface_definitions = ast.get("interface_definitions", [])
        self.driver_definitions = ast.get("driver_definitions", [])
        self.test_case_definitions = ast.get("test_case_definitions", [])


class Task:

    def __init__(self, definition):
        self.definition = definition
        #self.drivers = named_definitions(definition.drivers)
        self.interfaces = OrderedDict(
                (d.name, Interface(d))
                for d in definition.interface_definitions
        )
        #self.test_cases = named_definitions(definition.test_cases)
