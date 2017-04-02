class Expression:
    pass


class IntLiteralExpression:

    def __init__(self, ast):
        self.value = int(ast)
