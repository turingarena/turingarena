class ProtocolNode:

    def __init__(self, ast):
        pass

    @classmethod
    def get_node_type(cls):
        return cls.node_type


class InputOutputStep(ProtocolNode):

    def __init__(self, ast):
        super().__init__(ast)
        self.variables = ast.variables


class InputStep(InputOutputStep):

    node_type = "input"


class OutputStep(InputOutputStep):

    node_type = "output"


class CallStep(ProtocolNode):

    node_type = "call"

    def __init__(self, ast):
        super().__init__(ast)
        self.return_value = ast.return_value
        self.function_name = ast.function_name
        self.parameters = ast.parameters


class ForNode(ProtocolNode):

    node_type = "for"

    def __init__(self, ast):
        super().__init__(ast)
        self.index = ast.index
        self.range = ast.range
        self.steps = ast.steps


class SwitchNode(ProtocolNode):

    node_type = "switch"

    def __init__(self, ast):
        super().__init__(ast)
        self.expression = ast.expression
        self.cases = ast.cases


class SwitchCase:

    def __init__(self, ast):
        self.ast = ast
        self.value = ast.value
