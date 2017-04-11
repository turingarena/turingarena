class Expression:

    @classmethod
    def get_expression_type(cls):
        return cls.expression_type

    def as_simple_lvalue(self, scope, indexes):
        raise ValueError("not a simple lvalue")

class VariableExpression(Expression):

    expression_type = "variable"

    def __init__(self, ast):
        self.variable_name = ast.variable_name
        self.indexes = ast.indexes

    def as_simple_lvalue(self, scope, indexes):
        variable = scope[self.variable_name]
        if len(variable.array_dimensions) != len(indexes):
            raise ValueError("wrong number of dimensions")
        for i, index in enumerate(indexes):
            dim = variable.array_dimensions[i]
            if index.range.start != dim.start:
                raise ValueError("invalid index")
            if index.range.end != dim.end:
                raise ValueError("invalid index")
        return variable

    def __eq__(self, other):
        return (
            isinstance(other, VariableExpression) and
            other.variable_name == self.variable_name and
            other.indexes == self.indexes
        )


class IntLiteralExpression(Expression):

    expression_type = "int_literal"

    def __init__(self, ast):
        self.value = int(ast)

    def __eq__(self, other):
        return (
            isinstance(other, IntLiteralExpression) and
            other.value == self.value
        )
