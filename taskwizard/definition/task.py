from taskwizard.definition.declarations import named_definitions
from taskwizard.definition.syntax import AbstractSyntaxNode


class TaskDefinition(AbstractSyntaxNode):

    grammar_production = "task_definition"
    grammar = """
        task_definition =
        {
        | interfaces+:interface_definition
        | drivers+:driver_definition
        | test_cases+:test_case_definition
        }* $ ;
    """


class Task:

    def __init__(self, definition):
        self.definition = definition
        self.drivers = named_definitions(definition.drivers)
        self.interfaces = named_definitions(definition.interfaces)
        self.test_cases = named_definitions(definition.test_cases)
