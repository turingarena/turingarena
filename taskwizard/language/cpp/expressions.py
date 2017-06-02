from taskwizard.generation.expressions import AbstractExpressionGenerator


class ExpressionGenerator(AbstractExpressionGenerator):
    pass


def generate_expression(scope, expression):
    return ExpressionGenerator(scope).generate(expression)
