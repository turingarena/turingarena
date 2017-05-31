from taskwizard.language.cpp.types import generate_base_type
from taskwizard.generation.types import TypeVisitor


class DeclaratorGenerator(TypeVisitor):

    def __init__(self, declarator):
        self.declarator = declarator

    def visit_array_type(self, type):
        return '*' * len(type.dimensions) + self.declarator.name


def generate_declarator(declaration, declarator):
    return DeclaratorGenerator(declarator).visit(declaration.type)


def generate_declarators(declaration, scope):
    for declarator in declaration.declarators:
        yield generate_declarator(declaration, declarator)
        if declarator.name in scope:
            raise ValueError("already defined: %s" % declarator.name)
        scope[declarator.name] = declaration


def generate_declaration(declaration, scope):
    yield '{base_type} {declarators};'.format(
        base_type=generate_base_type(declaration.type),
        declarators=', '.join(generate_declarators(declaration, scope)),
    )


def generate_parameter(parameter):
    return '{base_type} {declarator}'.format(
        base_type=generate_base_type(parameter.type),
        declarator=generate_declarator(parameter, parameter.declarator),
    )