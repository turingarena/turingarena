class TypeBuilder:
    def build(self, t):
        return t.accept(self)

    def visit_scalar_type(self, t):
        return "scalar({base})".format(base=BaseTypeBuilder().build(t))

    def visit_array_type(self, t):
        return "array({item_type})".format(
            item_type=self.build(t.item_type),
        )


class BaseTypeBuilder:
    def build(self, t):
        return t.accept(self)

    def visit_scalar_type(self, t):
        return {
            "int": "int",
            "int64": "int",
            "string": "str",
        }[t.base]
