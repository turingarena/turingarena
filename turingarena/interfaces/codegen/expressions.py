from turingarena.interfaces.visitor import accept_expression


class DefaultLeftValueBuilder:
    def __init__(self, right_value_builder):
        self.right_value_builder = right_value_builder

    def visit_variable_expression(self, expr):
        return expr.variable_name

    def visit_subscript_expression(self, expr):
        array = accept_expression(expr.array, visitor=self)
        subscript = self.right_value_builder(expr.index)
        return array + '[' + subscript + ']'

    def visit_any_expression(self, expr):
        return self.on_right_value(expr)

    def on_right_value(self, expr):
        return self.right_value_builder(expr)


class DefaultRightValueBuilder:
    def __init__(self, left_value_builder):
        self.left_value_builder = left_value_builder

    def visit_int_literal_expression(self, expr):
        assert isinstance(expr.int_literal, str)
        return expr.int_literal

    def visit_bool_literal_expression(self, expr):
        assert isinstance(expr.bool_literal, str)
        if expr.bool_literal == "False":
            return "false"
        elif expr.bool_literal == "True":
            return "true"

    def visit_any_expression(self, expr):
        return self.on_left_value(expr)

    def on_left_value(self, expr):
        return self.left_value_builder(expr)
