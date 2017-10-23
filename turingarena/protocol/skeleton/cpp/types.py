from turingarena.protocol.visitor import accept_type_expression


class TypeExpressionBuilder:
    def visit_array_type(self, t):
        return build_type_expression(t.item_type) + '*'

    def visit_scalar_type(self, t):
        return {
            "int": "int",
            "int64": "long long int",
            "bool" : "bool"
        }[t.base]


def build_type_expression(type_expression):
    if type_expression is None:
        return "void"
    return accept_type_expression(type_expression, visitor=TypeExpressionBuilder())
