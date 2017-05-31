from taskwizard.generation.expressions import VariableExpressionVisitor
from taskwizard.generation.types import TypeVisitor


class FormatGenerator(TypeVisitor):

    def visit_array_type(self, type):
        return {
            "int": "%d",
            "int64": "%lld",
        }[type.base_type]


def generate_format(expression, scope):
    declaration = VariableExpressionVisitor(scope).visit(expression)
    return FormatGenerator().visit(declaration.type)
