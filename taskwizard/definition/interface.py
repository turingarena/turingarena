from taskwizard.definition.grammar import AbstractSyntaxNode


class InterfaceDefinition(AbstractSyntaxNode):

    def __init__(self, ast):
        self.name = ast.name
        self.raw = ast.raw is not None
        self.variable_definitions = ast.get("variables", [])
        self.function_definitions = ast.get("functions", [])
        self.callback_function_definitions = ast.get("callback_functions", [])


syntax_nodes = (
    InterfaceDefinition,
)