class StatementVisitor:

    def visit(self, statement):
        method = getattr(self, "visit_%s" % statement.parseinfo.rule)
        yield from method(statement)