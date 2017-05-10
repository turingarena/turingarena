from taskwizard.definition.common import Identifier
from taskwizard.definition.function import FunctionDefinition
from taskwizard.definition.protocol import ProtocolStatementDefinition
from taskwizard.definition.syntax import AbstractSyntaxNode
from taskwizard.definition.variable import VariableDefinition


class InterfaceDefinition(AbstractSyntaxNode):

    grammar = """
        interface_definition =
            'interface' name:identifier '{'

            {
            | 'raw' ~ raw:`true` ';'
            | variables+:global_variable_declaration
            | functions+:function_declaration
            | callback_functions+:function_declaration
            | main_definition:main_definition
            }*

            '}'
        ;

        global_variable_declaration = 'global' @:variable_declaration ;

        main_definition =
            'main' ~ '{'
                {protocol_statement}*
            '}' ;
    """
    grammar_deps = lambda: [Identifier, VariableDefinition, FunctionDefinition, ProtocolStatementDefinition]

    def __init__(self, ast):
        self.name = ast.name
        self.raw = ast.raw is not None
        self.variable_definitions = ast.get("variables", [])
        self.function_definitions = ast.get("functions", [])
        self.callback_function_definitions = ast.get("callback_functions", [])
