from taskwizard.definition.declarations import named_definitions
from taskwizard.definition.syntax import AbstractSyntaxNode


class ModuleDefinition(AbstractSyntaxNode):

    grammar = """
        module_definition =
            'module' name:identifier '{'
            {
            | 'source' source:STRING ';'
            | 'language' language:STRING ';'
            | variables+:variable_declaration
            }*
            '}'
            ;
    """


class Module:

    def __init__(self, definition):
        self.name = definition.name
        self.source = definition.source
        self.language = definition.language
        self.variables = named_definitions(definition.variables)
        self.functions = named_definitions(definition.functions)

        if self.source is None:
            raise ValueError("No source specified for module '%s'" % self.name)
