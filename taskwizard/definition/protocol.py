from taskwizard.definition.grammar import AbstractSyntaxNode


class Statement(AbstractSyntaxNode):
    pass


class InputOutputStatement(Statement):

    def __init__(self, ast):
        super().__init__(ast)
        self.variables = ast.variables


class InputStatement(InputOutputStatement):
    pass


class OutputStatement(InputOutputStatement):
    pass


class CallStatement(AbstractSyntaxNode):

    def __init__(self, ast):
        super().__init__(ast)
        self.return_value = ast.return_value
        self.function_name = ast.function_name
        self.parameters = ast.parameters


class ForIndex:

    def __init__(self, name, range):
        self.name = name
        self.range = range


class ForStatement(AbstractSyntaxNode):

    def __init__(self, ast):
        super().__init__(ast)
        self.index = ForIndex(ast.index, ast.range)
        self.statements = ast.statements


class SwitchStatement(AbstractSyntaxNode):

    def __init__(self, ast):
        super().__init__(ast)
        self.expression = ast.expression
        self.cases = ast.cases


class SwitchCase(AbstractSyntaxNode):

    def __init__(self, ast):
        self.value = ast.value


syntax_nodes = (
    Statement,
    InputStatement,
    OutputStatement,
    CallStatement,
    ForStatement,
    SwitchStatement,
    SwitchCase,
)
