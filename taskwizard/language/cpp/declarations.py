from taskwizard.language.cpp.types import generate_base_type


class DeclaratorGenerator:

    def generate(self, type, declarator):
        method = getattr(self, "generate_%s" % type.parseinfo.rule)
        return method(type, declarator)

    def generate_array_type(self, type, declarator):
        return '*' * len(type.dimensions) + declarator.identifier


generator = DeclaratorGenerator()


def generate_declarator(type, declarator):
    return generator.generate(type, declarator)


def generate_declaration(declaration):
    yield '{base_type} {declarators};'.format(
        base_type=generate_base_type(declaration.type),
        declarators=', '.join(
            generate_declarator(declaration.type, d)
            for d in declaration.declarators
        ),
    )


def generate_parameter(parameter):
    return '{base_type} {declarator}'.format(
        base_type=generate_base_type(parameter.type),
        declarator=generate_declarator(parameter.type, parameter.declarator),
    )