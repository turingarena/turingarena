class BaseTypeGenerator:

    def generate(self, type):
        method = getattr(self, "generate_%s" % type.parseinfo.rule)
        return method(type)

    def generate_array_type(self, e):
        return e.base_type

    def generate_variable_expression(self, e):
        return e.variable_name + ''.join('[' + self.generate(i) + ']' for i in e.indexes)


generator = BaseTypeGenerator()


def generate_base_type(type):
    return generator.generate(type)
