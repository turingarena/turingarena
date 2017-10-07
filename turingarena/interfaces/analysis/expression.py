from turingarena.interfaces.analysis.types import ScalarType


class ExpressionCompiler:
    def __init__(self, scope):
        self.scope = scope

    def compile(self, expr):
        expr.accept(self)

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
        self.compile(expr.array)
        self.compile(expr.index)

        if expr.index.type.base != "int":
            raise ValueError("invalid index expression")

        expr.type = expr.array.type.item_type

    def visit_variable_expression(self, expr):
        expr.variable_declaration = self.scope[expr.variable_name]
        expr.type = expr.variable_declaration.type

    def set_integer_type(self, expr):
        if expr.left.type.base != "int64" and expr.left.type.base != "int":
            raise ValueError("left operand is not an integer")
        if expr.right.type.base != "int64" and expr.right.type.base != "int":
            raise ValueError("right operand is not an integer")

        if (expr.left.type.base == "int64" and expr.right.type.base == "int64") or \
            (expr.left.type.base == "int" and expr.right.type.base == "int64") or \
            (expr.left.type.base == "int64" and expr.right.type.base == "int"):
            expr.type = ScalarType("int64")
        else:
            expr.type = ScalarType("int")

    def visit_addition_expression(self, expr):
        self.compile(expr.left)
        self.compile(expr.right)
        self.set_integer_type(expr)

    def visit_subtraction_expression(self, expr):
        self.compile(expr.left)
        self.compile(expr.right)
        self.set_integer_type(expr)

    def visit_multiplication_expression(self, expr):
        self.compile(expr.left)
        self.compile(expr.right)
        self.set_integer_type(expr)

    def visit_division_expression(self, expr):
        self.compile(expr.left)
        self.compile(expr.right)
        self.set_integer_type(expr)

    def visit_and_expression(self, expr):
        self.compile(expr.left)
        self.compile(expr.right)
        expr.type = ScalarType("bool")
        
    def visit_or_expression(self, expr):
        self.compile(expr.left)
        self.compile(expr.right)
        expr.type = ScalarType("bool")
        
    def visit_not_expression(self, expr):
        self.compile(expr.right)
        expr.type = ScalarType("bool")
        
    def visit_lesser_expression(self, expr):
        self.compile(expr.left)
        self.compile(expr.right)
        expr.type = ScalarType("bool")
        
    def visit_equality_expression(self, expr):
        self.compile(expr.left)
        self.compile(expr.right)
        expr.type = ScalarType("bool")
        

def compile_expression(e, scope):
    ExpressionCompiler(scope).compile(e)


def compile_range(range, scope):
    compile_expression(range.start, scope=scope)
    compile_expression(range.end, scope=scope)
