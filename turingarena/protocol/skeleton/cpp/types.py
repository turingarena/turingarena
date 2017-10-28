from turingarena.protocol.visitor import accept_type_expression


class TypeExpressionBuilder:
    def visit_array_type(self, t):
        return build_type_expression(t.item_type) + '*'

    def visit_scalar_type(self, t):
        return {
            int: "int",
            bool : "bool",
        }[t.base_type]


def build_type_expression(type_expression):
    if type_expression is None:
        return "void"
    return accept_type_expression(type_expression, visitor=TypeExpressionBuilder())
