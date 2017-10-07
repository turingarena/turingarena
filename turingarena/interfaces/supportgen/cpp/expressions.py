from turingarena.interfaces.visitor import accept_expression

from turingarena.interfaces.codegen.expressions import AbstractExpressionGenerator


class ExpressionGenerator(AbstractExpressionGenerator):
    pass


def generate_expression(expression):
    return accept_expression(expression, visitor=ExpressionGenerator())
