class AbstractExpressionGenerator:

    def generate(self, expr):
        return expr.accept(self)

    def visit_int_literal_expression(self, expr):
        return str(expr.value)

    def visit_variable_expression(self, expr):
        return expr.variable_name

    def visit_subscript_expression(self, expr):
        return self.generate(expr.array) + '[' + self.generate(expr.index) + ']'
