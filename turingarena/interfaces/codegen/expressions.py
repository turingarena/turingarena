class AbstractExpressionGenerator:
    def generate(self, expr):
        return expr.accept(self)

    def visit_int_literal_expression(self, expr):
        assert isinstance(expr.int_literal, str)
        return expr.int_literal

    def visit_bool_literal_expression(self, expr):
        assert isinstance(expr.bool_literal, str)
        if expr.bool_literal == "False":
            return "false"
        elif expr.bool_literal == "True":
            return "true"

    def visit_variable_expression(self, expr):
        return expr.variable_name

    def visit_subscript_expression(self, expr):
        return self.generate(expr.array) + '[' + self.generate(expr.index) + ']'
