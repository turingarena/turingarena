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


class ProtocolStatement:

    def __init__(self, definition):
        pass

    @staticmethod
    def create(definition):
        for name, cls in Protocol.cls_map.items():
            if isinstance(definition, cls.definition_cls):
                return cls(definition)

    @classmethod
    def get_statement_type(cls):
        return cls.statement_type

    def get_free_variables(self, scope, indexes):
        return []

    def get_arrays_to_allocate(self, scope, indexes):
        return []


class InputOutputStatementDefinition(AbstractSyntaxNode):

    def __init__(self, ast):
        self.variables = ast.variables


class InputOutputStatement(ProtocolStatement):

    def __init__(self, definition):
        self.variables = definition.variables

    def get_free_variables(self, scope, indexes):
        for variable in self.variables:
            yield variable.as_simple_lvalue(scope, indexes)


class InputStatementDefinition(InputOutputStatementDefinition):

    grammar = """
        input_statement =
        'input' ~ variables:','.{ expression }* ';'
        ;
    """
    grammar_deps = lambda: [Expression]


class InputStatement(InputOutputStatement):

    statement_type = "input"
    definition_cls = InputStatementDefinition


class OutputStatementDefinition(InputOutputStatementDefinition):

    grammar = """
        output_statement =
        'output' ~ variables:','.{ expression }* ';'
        ;
    """
    grammar_deps = lambda: [Expression]


class OutputStatement(InputOutputStatement):

    statement_type = "output"
    definition_cls = OutputStatementDefinition


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


class CallStatement(ProtocolStatement):

    statement_type = "call"
    definition_cls = CallStatementDefinition

    def __init__(self, definition):
        self.return_value = definition.return_value
        self.function_name = definition.function_name
        self.parameters = definition.parameters


class ForIndex:

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
        self.index = ForIndex(ast.index, ast.range)
        self.statements = ast.statements


class ForStatement(ProtocolStatement):

    statement_type = "for"
    definition_cls = ForStatementDefinition

    def __init__(self, definition):
        self.index = definition.index
        self.statements = [
            ProtocolStatement.create(s) for s in definition.statements
        ]

    def get_free_variables(self, scope, indexes):
        for statement in self.statements:
            yield from statement.get_free_variables(scope, indexes + [self.index])

    def get_arrays_to_allocate(self, scope, indexes):
        for var in self.get_free_variables(scope, indexes):
            yield (self, var, indexes)
        for statement in self.statements:
            yield from statement.get_arrays_to_allocate(scope, indexes + [self.index])


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


class SwitchStatement(ProtocolStatement):

    statement_type = "switch"
    definition_cls = SwitchStatementDefinition

    def __init__(self, definition):
        self.expression = definition.expression
        self.cases = [
            SwitchCase(c) for c in definition.cases
        ]


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


class SwitchCase:

    def __init__(self, definition):
        self.definition = definition
