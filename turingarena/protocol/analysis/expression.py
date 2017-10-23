from turingarena.protocol.visitor import accept_expression

from turingarena.protocol.analysis.types import ScalarType


class ExpressionCompiler:
    def __init__(self, scope):
        self.scope = scope

    def visit_int_literal_expression(self, expr):
        expr.int_value = int(expr.int_literal)
        expr.type = ScalarType("int")

    def visit_bool_literal_expression(self, expr):
        if expr.bool_literal == "False":
            expr.bool_value = False 
        elif expr.bool_literal == "True":
            expr.bool_value = True 
        else:
            ValueError("Invalid boolean")
        expr.type = ScalarType("bool")

    def visit_subscript_expression(self, expr):
        accept_expression(expr.array, visitor=self)
        accept_expression(expr.index, visitor=self)

        if expr.index.type.base != "int":
            raise ValueError("invalid index expression")

        expr.type = expr.array.type.item_type

    def visit_variable_expression(self, expr):
        expr.variable_declaration = self.scope[expr.variable_name]
        expr.type = expr.variable_declaration.type


def compile_expression(expr, scope):
    accept_expression(expr, visitor=ExpressionCompiler(scope))
