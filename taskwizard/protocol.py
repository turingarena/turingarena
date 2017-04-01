class ProtocolStep:

    def __init__(self, ast):
        pass


class InputOutputStep(ProtocolStep):

    def __init__(self, ast):
        super().__init__(ast)
        self.items = ast


class InputStep(InputOutputStep):
    pass


class OutputStep(InputOutputStep):
    pass


class CallStep(ProtocolStep):

    def __init__(self, ast):
        super().__init__(ast)
        self.return_value = ast.return_value
        self.function_name = ast.function_name
        self.parameters = ast.parameters
