from turingarena.interfaces.visitor import accept_type_expression


class BaseTypeGenerator:
    def visit_array_type(self, t):
        return generate_base_type(t.item_type)

    def visit_scalar_type(self, t):
        return {
            "int": "int",
            "int64": "long long int",
            "bool" : "bool"
        }[t.base]


def generate_base_type(type_expression):
    if type_expression is None:
        return "void"
    return accept_type_expression(type_expression, visitor=BaseTypeGenerator())
