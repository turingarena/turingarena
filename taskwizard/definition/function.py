from taskwizard.definition.syntax import AbstractSyntaxNode


class FunctionDefinition(AbstractSyntaxNode):

    grammar = """
        function_declaration =
        'function' return_type:return_type name:identifier '(' parameters:','.{parameter}* ')' ';'
        ;
    """

    def __init__(self, ast):
        self.name = ast.name
        self.return_type = ast.return_type
        self.parameters = ast.parameters
