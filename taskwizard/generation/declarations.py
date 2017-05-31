def process_declaration(declaration, scope):
    for declarator in declaration.declarators:
        yield declarator
        add_to_scope(scope, declarator, declaration)


def add_to_scope(scope, declarator, declaration):
    if declarator.name in scope:
        raise ValueError("already defined: %s" % declarator.name)
    scope[declarator.name] = declaration
