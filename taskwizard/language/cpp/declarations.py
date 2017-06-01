from taskwizard.generation.types import TypeVisitor
from taskwizard.language.cpp.types import generate_base_type


class DeclaratorBuildingTypeVisitor(TypeVisitor):

    def __init__(self, declarator):
        self.declarator = declarator

    def visit_array_type(self, type):
        return '*' * len(type.dimensions) + self.declarator.name


def build_declarator(declaration, declarator):
    return DeclaratorBuildingTypeVisitor(declarator).visit(declaration.type)


def generate_declarators(declaration, scope):
    for declarator in scope.process_declarators(declaration):
        yield build_declarator(declaration, declarator)


def build_declaration(declaration, scope):
    yield '{base_type} {declarators};'.format(
        base_type=generate_base_type(declaration.type),
        declarators=', '.join(generate_declarators(declaration, scope)),
    )


# TODO: use a scope for parameters, at least to ensure no name clash
def build_parameter(parameter):
    return '{base_type} {declarator}'.format(
        base_type=generate_base_type(parameter.type),
        declarator=build_declarator(parameter, parameter.declarator),
    )