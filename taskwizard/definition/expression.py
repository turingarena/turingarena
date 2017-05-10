from taskwizard.definition.common import Identifier, Literals
from taskwizard.definition.syntax import AbstractSyntaxNode


class Expression(AbstractSyntaxNode):

    grammar = """
        expression =
            | variable_expression
            | int_literal_expression
            ;
    """

    grammar_deps = lambda: [ VariableExpression, IntLiteralExpression ]

    @classmethod
    def get_expression_type(cls):
        return cls.expression_type

    def as_simple_lvalue(self, scope, indexes):
        raise ValueError("not a simple lvalue")


class RangeExpression(AbstractSyntaxNode):

    grammar = """
        range_expression =
            start:expression '..' end:expression
            ;
    """
    grammar_deps = lambda: [ Expression ]

    def __init__(self, ast):
        self.start = ast.start
        self.end = ast.end


class VariableExpression(Expression):

    expression_type = "variable"

    grammar = """
        variable_expression =
        variable_name:identifier
        indexes:{ variable_expression_index }*
        ;

        variable_expression_index = '[' @:expression ']' ;
    """
    grammar_deps = lambda: [Identifier]

    def __init__(self, ast):
        self.variable_name = ast.variable_name
        self.indexes = ast.indexes

    def as_simple_lvalue(self, scope, indexes):
        variable = scope[self.variable_name]
        if len(variable.array_dimensions) != len(indexes):
            raise ValueError("wrong number of dimensions")
        for i, index in enumerate(indexes):
            dim = variable.array_dimensions[i]
            if index.range.start != dim.start:
                raise ValueError("invalid index")
            if index.range.end != dim.end:
                raise ValueError("invalid index")
        return variable

    def __eq__(self, other):
        return (
            isinstance(other, VariableExpression) and
            other.variable_name == self.variable_name and
            other.indexes == self.indexes
        )


class IntLiteralExpression(Expression):

    expression_type = "int_literal"

    grammar = "int_literal_expression = value:INT;"
    grammar_deps = lambda: [Literals]

    def __init__(self, ast):
        self.value = int(ast.value)

    def __eq__(self, other):
        return (
            isinstance(other, IntLiteralExpression) and
            other.value == self.value
        )
