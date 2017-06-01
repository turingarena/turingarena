class TypeVisitor:

    def visit(self, t):
        method = getattr(self, "visit_%s" % t.parseinfo.rule)
        return method(t)


class BaseTypeExtractor(TypeVisitor):

    def visit_array_type(self, t):
        return self.visit(t.item_type)

    def visit_scalar_type(self, t):
        return t.base
