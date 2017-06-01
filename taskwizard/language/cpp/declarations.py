from taskwizard.grammar import SyntaxVisitor
from taskwizard.language.cpp.types import generate_base_type


class DeclaratorBuilder(SyntaxVisitor):

    def __init__(self, declarator):
        self.declarator = declarator

    def visit_scalar_type(self, type):
        return self.declarator.name

    def visit_array_type(self, type):
        return '*' + self.visit(type.item_type)


def build_declarator(declaration, declarator):
    return DeclaratorBuilder(declarator).visit(declaration.type)


def generate_declarators(declaration, scope):
    for declarator in scope.process_declarators(declaration):
        yield build_declarator(declaration, declarator)


def build_declaration(declaration, scope):
    return '{base_type} {declarators};'.format(
        base_type=generate_base_type(declaration.type),
        declarators=', '.join(generate_declarators(declaration, scope)),
    )


# TODO: use a scope for parameters, at least to ensure no name clash
def build_parameter(parameter):
    return '{base_type} {declarator}'.format(
        base_type=generate_base_type(parameter.type),
        declarator=build_declarator(parameter, parameter.declarator),
    )