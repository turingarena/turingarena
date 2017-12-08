def build_subscript(expression):
    array = build_expression(expression.array)
    index = build_expression(expression.index)
    return f"{array}[{index}]"


def build_expression(expression):
    builders = {
        "int_literal": lambda: f"{expression.value}",
        "bool_literal": lambda: f"{int(expression.value)}",
        "reference": lambda: f"{expression.variable.name}",
        "subscript": lambda: build_subscript(expression),
    }
    return builders[expression.expression_type]()
