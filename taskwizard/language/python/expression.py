from taskwizard.generation.expressions import AbstractExpressionGenerator


class DriverVariableExpressionBuilder:

    def __init__(self, expr):
        self.expr = expr

    def build(self, expr):
        return expr.accept(self)

    def visit_variable_declaration(self, declaration):
        if declaration.is_global:
            return "self.interface.{name}".format(
                name=self.expr.variable_name,
            )
        else:
            return self.build_local_dereference()

    def visit_parameter_declaration(self, declaration):
        return self.build_local_dereference()

    def build_local_dereference(self):
        return "{name}.value".format(
            name=self.expr.variable_name,
        )

    def visit_index_declaration(self, declaration):
        return self.expr.variable_name


class DriverExpressionBuilder(AbstractExpressionGenerator):

    def build(self, expr):
        return expr.accept(self)

    def visit_variable_expression(self, e):
        return DriverVariableExpressionBuilder(e).build(e.variable_declaration)


def build_driver_expression(expr):
    return DriverExpressionBuilder().build(expr)
