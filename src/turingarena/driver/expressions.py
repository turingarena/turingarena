class AbstractExpressionCodeGen:
    __slots__ = []

    def visit_Subscript(self, e):
        return f"{self.visit(e.array)}[{self.visit(e.index)}]"

    def visit_Variable(self, e):
        return e.name

    def visit_IntLiteral(self, e):
        return str(e.value)
