from turingarena.interfaces.codegen.expressions import AbstractExpressionGenerator


class ExpressionGenerator(AbstractExpressionGenerator):
    pass


def generate_expression(expression):
    return ExpressionGenerator().generate(expression)
