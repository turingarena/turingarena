from taskwizard.generation.expressions import ExpressionVisitor


class ExpressionGenerator(ExpressionVisitor):

    def visit_int_literal_expression(self, e):
        return str(e.value)

    def visit_variable_expression(self, e):
        return e.variable_name + ''.join(
            '[' + generate_expression(i) + ']'
            for i in e.indexes
        )


def generate_expression(expression):
    return ExpressionGenerator().visit(expression)
