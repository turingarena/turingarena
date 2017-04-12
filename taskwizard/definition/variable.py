from taskwizard.definition.common import Types, Identifier
from taskwizard.definition.expression import RangeExpression
from taskwizard.definition.syntax import AbstractSyntaxNode


class VariableDefinition(AbstractSyntaxNode):

    grammar_rule = "variable"
    grammar = """
        variable =
        type:type name:identifier {'[' array_dimensions+:range_expression ']'}*
        ;

        parameter =
        @:variable
        ;

        variable_declaration = @:variable ';' ;
    """
    grammar_deps = lambda: [Types, Identifier, RangeExpression]

    def __init__(self, ast):
        self.name = ast.name
        self.type = ast.type
        self.array_dimensions = ast.get("array_dimensions", [])


class Variable:

    def __init__(self, definition):
        self.definition = definition
        self.name = definition.name
        self.type = definition.type
        self.array_dimensions = definition.array_dimensions
