from taskwizard.definition.declarations import named_definitions
from taskwizard.definition.syntax import AbstractSyntaxNode


class FunctionDefinition(AbstractSyntaxNode):

    grammar = """
        function_declaration =
        [callback:'callback'] return_type:return_type name:identifier '(' parameters:','.{parameter}* ')' ';'
        ;
    """

    def is_callback(self):
        return hasattr(self, "callback")


class Function:

    def __init__(self, definition):
        self.definition = definition
