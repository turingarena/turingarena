from taskwizard.definition.declarations import named_definitions


class Interface:

    def __init__(self, ast):
        self.name = ast.name
        self.variables = named_definitions(ast.variables)
        self.functions = named_definitions(ast.functions)
        self.callback_functions = named_definitions(ast.callback_functions)
        self.protocols = named_definitions(ast.protocols)
