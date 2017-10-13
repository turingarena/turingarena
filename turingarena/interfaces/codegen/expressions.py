from abc import abstractmethod

from turingarena.interfaces.visitor import accept_expression


class AbstractReferenceExpressionBuilder:
    def visit_variable_expression(self, expr):
        return expr.variable_name

    def visit_subscript_expression(self, expr):
        array = accept_expression(expr.array, visitor=self)
        subscript = self.build_value(expr.index)
        return array + '[' + subscript + ']'

    @abstractmethod
    def build_value(self, expr):
        pass


class AbstractValueExpressionBuilder:
    def visit_int_literal_expression(self, expr):
        assert isinstance(expr.int_literal, str)
        return expr.int_literal

    def visit_bool_literal_expression(self, expr):
        assert isinstance(expr.bool_literal, str)
        if expr.bool_literal == "False":
            return "false"
        elif expr.bool_literal == "True":
            return "true"
