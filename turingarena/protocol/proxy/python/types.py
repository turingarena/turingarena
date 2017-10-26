def build_type(type_expression):
    return repr(type_expression)


def build_optional_type(type_expression):
    if type_expression is None:
        return "None"
    return build_type(type_expression)
