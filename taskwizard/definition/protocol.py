from taskwizard.definition.common import Identifier
from taskwizard.definition.expression import Expression, RangeExpression
from taskwizard.definition.syntax import AbstractSyntaxNode


class ProtocolStatementDefinition(AbstractSyntaxNode):

    grammar = """
        protocol_statement =
        | input_statement
        | output_statement
        | call_statement
        | for_statement
        | switch_statement
        ;
    """
    grammar_deps = lambda: [
        InputStatementDefinition,
        OutputStatementDefinition,
        CallStatementDefinition,
        ForStatementDefinition,
        SwitchStatementDefinition,
    ]


class InputOutputStatementDefinition(AbstractSyntaxNode):

    def __init__(self, ast):
        self.variables = ast.variables


class InputStatementDefinition(InputOutputStatementDefinition):

    grammar = """
        input_statement =
        'input' ~ variables:','.{ expression }* ';'
        ;
    """
    grammar_deps = lambda: [Expression]


class OutputStatementDefinition(InputOutputStatementDefinition):

    grammar = """
        output_statement =
        'output' ~ variables:','.{ expression }* ';'
        ;
    """
    grammar_deps = lambda: [Expression]


class CallStatementDefinition(AbstractSyntaxNode):

    grammar = """
        call_statement =
        'call' ~ [ return_value:expression '='  ] function_name:identifier '(' parameters:','.{ expression }* ')' ';'
        ;
    """
    grammar_deps = lambda: [Expression, Identifier]

    def __init__(self, ast):
        self.return_value = ast.return_value
        self.function_name = ast.function_name
        self.parameters = ast.parameters


class ForIndexDefinition:

    def __init__(self, name, range):
        self.name = name
        self.range = range


class ForStatementDefinition(AbstractSyntaxNode):

    grammar = """
        for_statement =
        'for' ~ '(' index:identifier ':' range:range_expression ')' '{'
        statements:{protocol_statement}*
        '}'
        ;
    """
    grammar_deps = lambda: [ProtocolStatementDefinition, RangeExpression]

    def __init__(self, ast):
        self.index = ForIndexDefinition(ast.index, ast.range)
        self.statements = ast.statements


class SwitchStatementDefinition(AbstractSyntaxNode):

    grammar = """
        switch_statement =
        'switch' ~ '(' expression:expression ')' '{'
        cases:{ switch_case }*
        '}'
        ;
    """
    grammar_deps = lambda: [SwitchCaseDefinition, Expression]

    def __init__(self, ast):
        self.expression = ast.expression
        self.cases = ast.cases


class SwitchCaseDefinition(AbstractSyntaxNode):

    grammar = """
        switch_case =
        'case' '(' value:identifier ')' '{'
        statements:{protocol_statement}*
        '}'
        ;
    """
    grammar_deps = lambda: [ProtocolStatementDefinition, Identifier]

    def __init__(self, ast):
        self.value = ast.value
