class TypeVisitor:

    def visit(self, type):
        method = getattr(self, "visit_%s" % type.parseinfo.rule)
        return method(type)


class BaseTypeVisitor:

    def visit(self, base_type):
        method = getattr(self, "visit_%s" % type.parseinfo.rule)
        return method(base_type)
