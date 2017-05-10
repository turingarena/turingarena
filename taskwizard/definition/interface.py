from collections import OrderedDict

from taskwizard.definition.common import Identifier
from taskwizard.definition.function import FunctionDefinition, Function
from taskwizard.definition.protocol import Protocol, ProtocolDefinition
from taskwizard.definition.syntax import AbstractSyntaxNode
from taskwizard.definition.variable import VariableDefinition, Variable


class InterfaceDefinition(AbstractSyntaxNode):

    grammar = """
        interface_definition =
            'interface' name:identifier '{'

            {
            | variables+:variable_declaration
            | functions+:function_declaration
            | protocols+:protocol_declaration
            | callback_functions+:function_declaration
            }*

            '}'
        ;
    """
    grammar_deps = lambda: [Identifier, VariableDefinition, FunctionDefinition, ProtocolDefinition]

    def __init__(self, ast):
        self.name = ast.name
        self.variable_definitions = ast.get("variables", [])
        self.function_definitions = ast.get("functions", [])
        self.callback_function_definitions = ast.get("callback_functions", [])
        self.protocol_definitions = ast.get("protocols", [])


class Interface:

    def __init__(self, definition):
        self.definition = definition
        self.name = definition.name
        self.variables = OrderedDict(
                (d.name, Variable(d)) for d in definition.variable_definitions
        )
        self.functions = OrderedDict(
                (d.name, Function(d)) for d in definition.function_definitions
        )
        self.callback_functions = OrderedDict(
                (d.name, Function(d)) for d in definition.callback_function_definitions
        )
        self.named_protocols = OrderedDict(
                (d.name, Protocol(d)) for d in definition.protocol_definitions
                if d.name is not None
        )
        self.main_protocol = (
            [Protocol(d) for d in definition.protocol_definitions if d.name is None]
        )[0]

    def get_arrays_to_allocate(self, protocol):
        return protocol.get_arrays_to_allocate(self.variables)