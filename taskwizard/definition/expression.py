class Expression:

    @classmethod
    def get_expression_type(cls):
        return cls.expression_type


class VariableExpression(Expression):

    expression_type = "variable"

    def __init__(self, ast):
        self.variable_name = ast.variable_name
        self.indexes = ast.indexes


class IntLiteralExpression(Expression):

    expression_type = "int_literal"

    def __init__(self, ast):
        self.value = int(ast)
