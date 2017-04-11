class Protocol:

    def __init__(self, ast):
        self.steps = ast.steps
        self.name = ast.name

    def get_arrays_to_allocate(self, scope):
        for step in self.steps:
            yield from step.get_arrays_to_allocate(scope, [])

    def get_free_variables(self, scope):
        for step in self.steps:
            yield from step.get_free_variables(scope, [])


class ProtocolNode:

    def __init__(self, ast):
        pass

    @classmethod
    def get_node_type(cls):
        return cls.node_type

    def get_free_variables(self, scope, indexes):
        return []

    def get_arrays_to_allocate(self, scope, indexes):
        return []


class InputOutputStep(ProtocolNode):

    def __init__(self, ast):
        super().__init__(ast)
        self.variables = ast.variables

    def get_free_variables(self, scope, indexes):
        for variable in self.variables:
            yield variable.as_simple_lvalue(scope, indexes)


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


class ForIndex:

    def __init__(self, name, range):
        self.name = name
        self.range = range


class ForNode(ProtocolNode):

    node_type = "for"

    def __init__(self, ast):
        super().__init__(ast)
        self.index = ForIndex(ast.index, ast.range)
        self.steps = ast.steps

    def get_free_variables(self, scope, indexes):
        for step in self.steps:
            yield from step.get_free_variables(scope, indexes + [self.index])

    def get_arrays_to_allocate(self, scope, indexes):
        for var in self.get_free_variables(scope, indexes):
            yield (self, var, indexes)
        for step in self.steps:
            yield from step.get_arrays_to_allocate(scope, indexes + [self.index])

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
