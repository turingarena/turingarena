from taskwizard.generation.expressions import VariableExpressionVisitor
from taskwizard.generation.types import BaseTypeExtractor


def generate_format(expression, scope):
    declaration = VariableExpressionVisitor(scope).visit(expression)
    base_type = BaseTypeExtractor().visit(declaration.type)
    return {
        "int": "%d",
        "int64": "%lld",
    }[base_type]
