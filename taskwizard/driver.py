from grako.exceptions import FailedSemantics

from taskwizard.declarations import named_definitions


class Driver:

    def __init__(self, ast):
        self.name = ast.name
        self.source = ast.source
        self.language = ast.language
        self.global_variables = named_definitions(ast.global_variables)
        self.functions = named_definitions(ast.functions)

        if self.source is None:
            raise ValueError("No source specified for driver '%s'" % self.name)
