from turingarena.protocol.analysis.types import ScalarType


class ExpressionCompiler:
    def __init__(self, scope):
        self.scope = scope

    def compile_int_literal(self, expr):
        expr.int_value = int(expr.int_literal)
        expr.type = ScalarType("int")

    def compile_bool_literal(self, expr):
        expr.bool_value = bool(int(expr.bool_literal))
        expr.type = ScalarType("bool")

    def compile_subscript(self, expr):
        compile_expression(expr.array, scope=self.scope)
        compile_expression(expr.index, scope=self.scope)

        if expr.index.type.base != "int":
            raise ValueError("invalid index expression")

        expr.type = expr.array.type.item_type

    def compile_variable(self, expr):
        expr.variable_declaration = self.scope["var", expr.variable_name]
        expr.type = expr.variable_declaration.type


def compile_expression(expr, *, scope):
    compiler = ExpressionCompiler(scope)
    getattr(compiler, "compile_" + expr.expression_type)(expr)
