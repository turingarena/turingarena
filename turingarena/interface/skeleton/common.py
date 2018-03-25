class ExpressionBuilder:
    def build(self, e):
        return getattr(self, e.expression_type)(e)

    def int_literal(self, e):
        return f"{e.value}"

    def reference(self, e):
        subscripts = "".join(f"[{self.build(index)}]" for index in e.indices)
        return f"{e.variable_name}{subscripts}"
