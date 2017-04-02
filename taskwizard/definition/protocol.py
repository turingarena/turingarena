class ProtocolNode:

    def __init__(self, ast):
        pass


class InputOutputStep(ProtocolNode):

    def __init__(self, ast):
        super().__init__(ast)
        self.items = ast


class InputStep(InputOutputStep):
    pass


class OutputStep(InputOutputStep):
    pass


class CallStep(ProtocolNode):

    def __init__(self, ast):
        super().__init__(ast)
        self.return_value = ast.return_value
        self.function_name = ast.function_name
        self.parameters = ast.parameters


class ForNode(ProtocolNode):

    def __init__(self, ast):
        super().__init__(ast)
        self.index = ast.index
        self.range = ast.range


class SwitchNode(ProtocolNode):

    def __init__(self, ast):
        super().__init__(ast)
        self.expression = ast.expression
        self.cases = ast.cases


class SwitchCase:

    def __init__(self, ast):
        self.ast = ast
        self.value = ast.value
