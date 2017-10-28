from turingarena.protocol.visitor import accept_type_expression

from turingarena.protocol.skeleton.cpp.types import build_type_expression


class DeclaratorBuilder:
    def __init__(self, variable):
        self.variable = variable

    def visit_scalar_type(self, type_expression):
        return self.variable.name

    def visit_array_type(self, type_expression):
        return accept_type_expression(type_expression.item_type, visitor=self)


def build_declarator(declaration, variable):
    return accept_type_expression(declaration.type, visitor=DeclaratorBuilder(variable))


def generate_declarators(declaration):
    for variable in declaration.variables:
        yield build_declarator(declaration, variable)


def build_declaration(declaration):
    return '{base_type} {declarators};'.format(
        base_type=build_type_expression(declaration.type),
        declarators=', '.join(generate_declarators(declaration)),
    )


def build_parameter(parameter):
    return '{base_type} {declarator}'.format(
        base_type=build_type_expression(parameter.type),
        declarator=build_declarator(parameter, parameter),
    )
