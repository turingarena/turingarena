class ExpressionCompiler:

    def __init__(self, scope):
        self.scope = scope

    def compile(self, expr):
        expr.accept(self)

    def visit_int_literal_expression(self, expr):
        expr.value = int(expr.value)

    def visit_subscript_expression(self, expr):
        self.compile(expr.array)
        self.compile(expr.index)

    def visit_variable_expression(self, expr):
        expr.variable_declaration = self.scope[expr.variable_name]


def compile_expression(e, scope):
    ExpressionCompiler(scope).compile(e)


def compile_range(range, scope):
    compile_expression(range.start, scope=scope)
    compile_expression(range.end, scope=scope)
