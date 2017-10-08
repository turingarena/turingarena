from turingarena.interfaces.visitor import accept_type_expression

from turingarena.interfaces.supportgen.cpp.types import generate_base_type


class DeclaratorBuilder:
    def __init__(self, declarator):
        self.declarator = declarator

    def visit_scalar_type(self, type_expression):
        return self.declarator.name

    def visit_array_type(self, type_expression):
        return '*' + accept_type_expression(type_expression.item_type, visitor=self)


def build_declarator(declaration, declarator):
    return accept_type_expression(declaration.type, visitor=DeclaratorBuilder(declarator))


def generate_declarators(declaration):
    for declarator in declaration.declarators:
        yield build_declarator(declaration, declarator)


def build_declaration(declaration):
    return '{base_type} {declarators};'.format(
        base_type=generate_base_type(declaration.type),
        declarators=', '.join(generate_declarators(declaration)),
    )


def build_parameter(parameter):
    return '{base_type} {declarator}'.format(
        base_type=generate_base_type(parameter.type),
        declarator=build_declarator(parameter, parameter.declarator),
    )
