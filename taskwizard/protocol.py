class ProtocolStep:
    pass


class InputOutputStep(ProtocolStep):

    def __init__(self, items):
        self.items = items


class InputStep(InputOutputStep):
    pass


class OutputStep(InputOutputStep):
    pass


class CallStep(ProtocolStep):

    def __init__(self, ast):
        self.return_value = ast.return_value
        self.function_name = ast.function_name
        self.parameters = ast.parameters
