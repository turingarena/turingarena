class Variable:

    def __init__(self, ast):
        self.name = ast.name
        self.type = ast.type
        self.array_dimensions = ast.array_dimensions
