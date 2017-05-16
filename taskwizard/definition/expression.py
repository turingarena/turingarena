from taskwizard.definition.grammar import AbstractSyntaxNode


class Range(AbstractSyntaxNode):

    def __init__(self, ast):
        self.start = ast.start
        self.end = ast.end


class Expression(AbstractSyntaxNode):
    pass


class VariableExpression(Expression):

    def __init__(self, ast):
        self.variable_name = ast.variable_name
        self.indexes = ast.indexes

    def __eq__(self, other):
        return (
            isinstance(other, VariableExpression) and
            other.variable_name == self.variable_name and
            other.indexes == self.indexes
        )


class IntLiteralExpression(Expression):

    def __init__(self, ast):
        self.value = int(ast.value)

    def __eq__(self, other):
        return (
            isinstance(other, IntLiteralExpression) and
            other.value == self.value
        )


syntax_nodes = (
    Range,
    Expression,
    VariableExpression,
    IntLiteralExpression,
)