def process_declarators(declaration, *, scope):
    for declarator in declaration.declarators:
        scope[declarator.name] = declaration


def process_simple_declaration(declaration, *, scope):
    scope[declaration.declarator.name] = declaration
