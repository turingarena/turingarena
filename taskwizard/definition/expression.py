class Expression:
    pass


class VariableExpression(Expression):

    def __init__(self, ast):
        self.variable_name = ast.variable_name
        self.indexes = ast.indexes


class IntLiteralExpression(Expression):

    def __init__(self, ast):
        self.value = int(ast)
