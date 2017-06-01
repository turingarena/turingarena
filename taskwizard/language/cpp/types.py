from taskwizard.grammar import SyntaxVisitor


class BaseTypeGenerator(SyntaxVisitor):

    def visit_array_type(self, t):
        return self.visit(t.item_type)

    def visit_scalar_type(self, t):
        return {
            "int": "int",
            "int64": "long long int",
        }[t.base]


def generate_base_type(type):
    return BaseTypeGenerator().visit(type)
