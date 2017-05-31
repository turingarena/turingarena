from taskwizard.generation.types import TypeVisitor


class BaseTypeGenerator(TypeVisitor):

    def visit_array_type(self, e):
        return {
            "int": "int",
            "int64": "long long int",
        }[e.base_type]


def generate_base_type(type):
    return BaseTypeGenerator().visit(type)
