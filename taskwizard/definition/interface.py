from taskwizard.definition.declarations import named_definitions
from taskwizard.definition.syntax import AbstractSyntaxNode


class InterfaceDefinition(AbstractSyntaxNode):

    grammar = """
        interface_definition =
            'interface' name:identifier '{'
            {
            | variables+:variable_declaration
            | functions+:function_declaration
            | callback_functions+:callback_function_declaration
            | protocols+:protocol_declaration
            }*
            '}'
        ;

        callback_function_declaration = 'callback' @:function_declaration ;
    """


class Interface:

    def __init__(self, definition):
        self.definition = definition
        self.name = definition.name
        self.variables = named_definitions(definition.variables)
        self.functions = named_definitions(definition.functions)
        self.callback_functions = named_definitions(definition.callback_functions)
        self.protocols = named_definitions(definition.protocols)

    def get_arrays_to_allocate(self, protocol):
        return protocol.get_arrays_to_allocate(self.variables)