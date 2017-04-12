from taskwizard.definition.declarations import named_definitions
from taskwizard.definition.syntax import AbstractSyntaxNode


class FunctionDefinition(AbstractSyntaxNode):

    grammar = """
        function_declaration =
        return_type:return_type name:identifier '(' parameters:','.{parameter}* ')' ';'
        ;
    """

    def __init__(self, ast):
        self.name = ast.name
        self.return_type = ast.return_type
        self.parameters = ast.parameters


class Function:

    def __init__(self, definition):
        self.definition = definition
        self.name = definition.name
        self.return_type = definition.return_type
        self.parameters = named_definitions(definition.parameters)
