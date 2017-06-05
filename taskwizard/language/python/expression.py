from taskwizard.generation.expressions import AbstractExpressionGenerator


class DriverVariableExpressionBuilder:

    def __init__(self, expr):
        self.expr = expr

    def build(self, expr):
        return expr.accept(self)

    def visit_global_declaration(self, declaration):
        return "self.data.{name}".format(
            name=self.expr.variable_name,
        )

    def visit_local_declaration(self, declaration):
        return "get_value({var})".format(
            var=self.expr.variable_name,
        )

    def visit_parameter_declaration(self, declaration):
        return self.expr.variable_name

    def visit_index_declaration(self, declaration):
        return self.expr.variable_name


class DriverAssignableVariableExpressionBuilder:

    def __init__(self, expr):
        self.expr = expr

    def build(self, expr):
        return expr.accept(self)

    def visit_global_declaration(self, declaration):
        return "self.data.{name}".format(
            name=self.expr.variable_name,
        )

    def visit_local_declaration(self, declaration):
        return "{var}".format(
            var=self.expr.variable_name,
        )


class DriverExpressionBuilder(AbstractExpressionGenerator):

    def build(self, expr):
        return expr.accept(self)

    def visit_variable_expression(self, e):
        declaration = self.scope[e.variable_name]
        return DriverVariableExpressionBuilder(e).build(declaration)


class DriverAssignableExpressionBuilder(AbstractExpressionGenerator):

    def build(self, expr):
        return expr.accept(self)

    def visit_variable_expression(self, e):
        declaration = self.scope[e.variable_name]
        return DriverAssignableVariableExpressionBuilder(e).build(declaration)


def build_driver_expression(scope, expr):
    return DriverExpressionBuilder(scope).build(expr)

def build_assignable_driver_expression(scope, expr):
    return DriverAssignableExpressionBuilder(scope).build(expr)
