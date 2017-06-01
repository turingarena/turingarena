class InterfaceItemVisitor:

    def visit(self, item):
        method = getattr(self, "visit_%s" % item.parseinfo.rule)
        return method(item)
