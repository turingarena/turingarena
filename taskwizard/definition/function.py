from taskwizard.definition.declarations import named_definitions


class Function:

    def __init__(self, ast):
        self.name = ast.name
        self.return_type = ast.return_type
        self.parameters = named_definitions(ast.parameters)
