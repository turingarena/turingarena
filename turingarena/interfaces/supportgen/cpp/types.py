class BaseTypeGenerator:
    def visit_array_type(self, t):
        return generate_base_type(t.item_type)

    def visit_scalar_type(self, t):
        return {
            "int": "int",
            "int64": "long long int",
            "bool" : "bool"
        }[t.base]


def generate_base_type(t):
    return t.accept(BaseTypeGenerator())
