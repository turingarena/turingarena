from taskwizard.generation.expressions import AbstractExpressionGenerator


class DriverVariableExpressionBuilder:

    def __init__(self, expr):
        self.expr = expr

    def build(self, expr):
        return expr.accept(self)

    def visit_global_declaration(self, declaration):
        return "self.interface.{name}".format(
            name=self.expr.variable_name,
        )

    def visit_local_declaration(self, declaration):
        return "{var}.value".format(
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
        return "{var}.value".format(
            var=self.expr.variable_name,
        )


class DriverExpressionBuilder(AbstractExpressionGenerator):

    def build(self, expr):
        return expr.accept(self)

    def visit_variable_expression(self, e):
        return DriverVariableExpressionBuilder(e).build(e.variable_declaration)


class DriverAssignableExpressionBuilder(AbstractExpressionGenerator):

    def build(self, expr):
        return expr.accept(self)

    def visit_variable_expression(self, e):
        return DriverAssignableVariableExpressionBuilder(e).build(e.variable_declaration)


def build_driver_expression(expr):
    return DriverExpressionBuilder().build(expr)

def build_assignable_driver_expression(expr):
    return DriverAssignableExpressionBuilder().build(expr)
