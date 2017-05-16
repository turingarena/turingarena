from taskwizard.definition.grammar import AbstractSyntaxNode


class FunctionDefinition(AbstractSyntaxNode):

    def __init__(self, ast):
        self.name = ast.name
        self.return_type = ast.return_type
        self.parameters = ast.parameters


syntax_nodes = (
    FunctionDefinition,
)