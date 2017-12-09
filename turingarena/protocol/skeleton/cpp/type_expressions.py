def build_declarator(value_type, name):
    if value_type is None:
        return name
    builders = {
        "scalar": lambda: name,
        "array": lambda: "*" + build_declarator(value_type.item_type, name),
    }
    return builders[value_type.meta_type]()


def build_type_specifier(value_type):
    if value_type is None:
        return "void"
    builders = {
        "scalar": lambda: {
            int: "int",
        }[value_type.base_type],
        "array": lambda: build_type_specifier(value_type.item_type)
    }
    return builders[value_type.meta_type]()


def build_full_type(value_type):
    return build_type_specifier(value_type) + build_declarator(value_type, "")
