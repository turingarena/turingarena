from taskwizard.definition.syntax import AbstractSyntaxNode


class VariableDefinition(AbstractSyntaxNode):

    grammar_rule = "variable"
    grammar = """
        variable =
        type:type name:identifier {'[' array_dimensions+:range ']'}*
        ;

        parameter =
        @:variable
        ;

        variable_declaration = @:variable ';' ;
    """


class Variable:

    def __init__(self, definition):
        self.definition = definition
        self.name = definition.name
        self.type = definition.type
        self.array_dimensions = definition.array_dimensions
