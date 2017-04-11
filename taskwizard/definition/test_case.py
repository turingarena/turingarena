from taskwizard.definition.declarations import named_definitions
from taskwizard.definition.syntax import AbstractSyntaxNode


class TestCaseDefinition(AbstractSyntaxNode):

    grammar = """
        test_case_definition::TestCase =
        'testcase' name:identifier '{'
        { phases+:test_phase_definition }*
        '}'
        ;

        test_phase_definition::TestPhase =
        'phase' name:identifier '{'
        {
        | 'driver' driver_name:identifier driver_command:command ';'
        | slots+:slot_definition ';'
        }*
        '}'
        ;

        slot_definition::TestPhaseSlot = 'slot' name:identifier 'interface' interface_name:identifier ;

        command =
        function_name:identifier '(' parameters:','.{ expression }* ')'
        ;
    """


class TestCase:

    def __init__(self, ast):
        self.name = ast.name
        self.phases = named_definitions(ast.phases)


class TestPhase:

    def __init__(self, ast):
        self.name = ast.name
        self.driver_name = ast.driver_name
        self.slots = named_definitions(ast.slots)


class TestPhaseSlot:

    def __init__(self, ast):
        self.name = ast.name
        self.interface_name = ast.interface_name
