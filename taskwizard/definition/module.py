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

    def __init__(self, ast):
        self.name = ast.name
        self.source = ast.source
        self.language = ast.language
