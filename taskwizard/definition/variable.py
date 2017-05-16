from taskwizard.definition.common import Types, Identifier
from taskwizard.definition.expression import RangeExpression
from taskwizard.definition.grammar import AbstractSyntaxNode


class VariableDefinition(AbstractSyntaxNode):

    def __init__(self, ast):
        self.name = ast.name
        self.type = ast.type
        self.array_dimensions = ast.get("array_dimensions", [])


syntax_nodes = (
    VariableDefinition,
)
