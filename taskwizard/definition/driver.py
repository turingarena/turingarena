from taskwizard.definition.declarations import named_definitions


class Driver:

    def __init__(self, ast):
        self.name = ast.name
        self.source = ast.source
        self.language = ast.language
        self.variables = named_definitions(ast.variables)
        self.functions = named_definitions(ast.functions)

        if self.source is None:
            raise ValueError("No source specified for driver '%s'" % self.name)
