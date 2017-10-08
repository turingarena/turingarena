from turingarena.interfaces.visitor import accept_type_expression


class TypeBuilder:

    def visit_scalar_type(self, type_expression):
        return "scalar({base})".format(
            base=build_base_type(type_expression)
        )

    def visit_array_type(self, type_expression):
        return "array({item_type})".format(
            item_type=build_type(type_expression.item_type),
        )


class BaseTypeBuilder:

    def visit_scalar_type(self, t):
        return {
            "int": "int",
            "int64": "int",
            "bool": "bool",
            "string": "str",
        }[t.base]


def build_base_type(type_expression):
    return accept_type_expression(type_expression, visitor=BaseTypeBuilder())


def build_type(type_expression):
    return accept_type_expression(type_expression, visitor=TypeBuilder())
