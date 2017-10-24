from turingarena.protocol.visitor import accept_type_expression


class TypeBuilder:
    def visit_scalar_type(self, type_expression):
        return "scalar({base})".format(
            base={
                "int": "int",
                "int64": "int",
                "bool": "bool",
                "string": "str",
            }[type_expression.base]
        )

    def visit_array_type(self, type_expression):
        return "array({item_type})".format(
            item_type=build_type_expression(type_expression.item_type),
        )


def build_type_expression(type_expression):
    return accept_type_expression(type_expression, visitor=TypeBuilder())


def build_optional_type_expression(type_expression):
    if type_expression is None:
        return "None"
    return build_type_expression(type_expression)
