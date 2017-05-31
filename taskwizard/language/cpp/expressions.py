class ExpressionGenerator:

    def generate(self, expression):
        method = getattr(self, "generate_%s" % expression.parseinfo.rule)
        return method(expression)

    def generate_int_literal_expression(self, e):
        return str(e.value)

    def generate_variable_expression(self, e):
        return e.variable_name + ''.join('[' + self.generate(i) + ']' for i in e.indexes)


generator = ExpressionGenerator()


def generate_expression(expression):
    return generator.generate(expression)
