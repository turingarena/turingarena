from taskwizard.definition.common import Identifier
from taskwizard.definition.expression import Expression, RangeExpression
from taskwizard.definition.syntax import AbstractSyntaxNode


class ProtocolDefinition(AbstractSyntaxNode):

    grammar = """
        protocol_declaration =
        'protocol' [name:identifier] '{'
        steps:protocol_nodes
        '}'
        ;

        protocol_nodes =
        {protocol_node}*
        ;
    """
    grammar_deps = lambda: [ProtocolNodeDefinition, Identifier]

    def __init__(self, ast):
        self.name = ast.name
        self.steps = ast.steps


class Protocol:

    def __init__(self, definition):
        self.definition = definition
        self.steps = [
            ProtocolNode.create(s) for s in definition.steps
        ]

    def get_arrays_to_allocate(self, scope):
        for step in self.steps:
            yield from step.get_arrays_to_allocate(scope, [])

    def get_free_variables(self, scope):
        for step in self.steps:
            yield from step.get_free_variables(scope, [])


class ProtocolNodeDefinition(AbstractSyntaxNode):

    grammar = """
        protocol_node =
        | input_step
        | output_step
        | call_step
        | for_node
        | switch_node
        ;
    """
    grammar_deps = lambda: [
        InputStepDefinition,
        OutputStepDefinition,
        CallStepDefinition,
        ForNodeDefinition,
        SwitchNodeDefinition,
    ]


class ProtocolNode:

    def __init__(self, definition):
        pass

    @staticmethod
    def create(definition):
        for name, cls in Protocol.cls_map.items():
            if isinstance(definition, cls.definition_cls):
                return cls(definition)

    @classmethod
    def get_node_type(cls):
        return cls.node_type

    def get_free_variables(self, scope, indexes):
        return []

    def get_arrays_to_allocate(self, scope, indexes):
        return []


class InputOutputStepDefinition(AbstractSyntaxNode):

    def __init__(self, ast):
        self.variables = ast.variables


class InputOutputStep(ProtocolNode):

    def __init__(self, definition):
        self.variables = definition.variables

    def get_free_variables(self, scope, indexes):
        for variable in self.variables:
            yield variable.as_simple_lvalue(scope, indexes)


class InputStepDefinition(InputOutputStepDefinition):

    grammar = """
        input_step =
        'input' ~ variables:','.{ expression }* ';'
        ;
    """
    grammar_deps = lambda: [Expression]


class InputStep(InputOutputStep):

    node_type = "input"
    definition_cls = InputStepDefinition


class OutputStepDefinition(InputOutputStepDefinition):

    grammar = """
        output_step =
        'output' ~ variables:','.{ expression }* ';'
        ;
    """
    grammar_deps = lambda: [Expression]


class OutputStep(InputOutputStep):

    node_type = "output"
    definition_cls = OutputStepDefinition


class CallStepDefinition(AbstractSyntaxNode):

    grammar = """
        call_step =
        'call' ~ [ return_value:expression '='  ] function_name:identifier '(' parameters:','.{ expression }* ')' ';'
        ;
    """
    grammar_deps = lambda: [Expression, Identifier]

    def __init__(self, ast):
        self.return_value = ast.return_value
        self.function_name = ast.function_name
        self.parameters = ast.parameters


class CallStep(ProtocolNode):

    node_type = "call"
    definition_cls = CallStepDefinition

    def __init__(self, definition):
        self.return_value = definition.return_value
        self.function_name = definition.function_name
        self.parameters = definition.parameters


class ForIndex:

    def __init__(self, name, range):
        self.name = name
        self.range = range


class ForNodeDefinition(AbstractSyntaxNode):

    grammar = """
        for_node =
        'for' ~ '(' index:identifier ':' range:range_expression ')' '{'
        steps:protocol_nodes
        '}'
        ;
    """
    grammar_deps = lambda: [RangeExpression, ProtocolDefinition]

    def __init__(self, ast):
        self.index = ForIndex(ast.index, ast.range)
        self.steps = ast.steps


class ForNode(ProtocolNode):

    node_type = "for"
    definition_cls = ForNodeDefinition

    def __init__(self, definition):
        self.index = definition.index
        self.steps = [
            ProtocolNode.create(s) for s in definition.steps
        ]

    def get_free_variables(self, scope, indexes):
        for step in self.steps:
            yield from step.get_free_variables(scope, indexes + [self.index])

    def get_arrays_to_allocate(self, scope, indexes):
        for var in self.get_free_variables(scope, indexes):
            yield (self, var, indexes)
        for step in self.steps:
            yield from step.get_arrays_to_allocate(scope, indexes + [self.index])


class SwitchNodeDefinition(AbstractSyntaxNode):

    grammar = """
        switch_node =
        'switch' ~ '(' expression:expression ')' '{'
        cases:{ switch_case }*
        '}'
        ;
    """
    grammar_deps = lambda: [SwitchCaseDefinition, Expression]

    def __init__(self, ast):
        self.expression = ast.expression
        self.cases = ast.cases


class SwitchNode(ProtocolNode):

    node_type = "switch"
    definition_cls = SwitchNodeDefinition

    def __init__(self, definition):
        self.expression = definition.expression
        self.cases = [
            SwitchCase(c) for c in definition.cases
        ]


class SwitchCaseDefinition(AbstractSyntaxNode):

    grammar = """
        switch_case =
        'case' '(' value:identifier ')' '{'
        steps:protocol_nodes
        '}'
        ;
    """
    grammar_deps = lambda: [ProtocolDefinition, Identifier]

    def __init__(self, ast):
        self.value = ast.value


class SwitchCase:

    def __init__(self, definition):
        self.definition = definition


Protocol.cls_map = {
    "input": InputStep,
    "output": OutputStep,
    "call": CallStep,
    "for": ForNode,
    "switch": SwitchNode,
}

