from taskwizard.generation.scope import Scope
from taskwizard.generation.utils import indent_all, indent
from taskwizard.grammar import SyntaxVisitor
from taskwizard.language.python.protocol import generate_driver_block


class GlobalPropertyGenerator(SyntaxVisitor):

    def __init__(self, declaration, declarator):
        self.declaration = declaration
        self.declarator = declarator

    def visit_scalar_type(self, t):
        args = {"name": self.declarator.name}
        yield
        yield "@property"
        yield "def {name}(self):".format(**args)
        yield from indent_all(generate_getter_body(self.declaration, self.declarator))
        yield
        yield "@{name}.setter".format(**args)
        yield "def {name}(self, value):".format(**args)
        yield from indent_all(generate_setter_body(self.declaration, self.declarator))

    def visit_array_type(self, t):
        args = {"name": self.declarator.name}
        yield
        yield "@property"
        yield "def {name}(self):".format(**args)
        yield from indent_all(generate_array_getter_body(self.declaration, self.declarator))


class SupportInterfaceItemGenerator(SyntaxVisitor):

    def __init__(self):
        self.global_scope = Scope()

    def visit_global_declaration(self, declaration):
        for declarator in self.global_scope.process_declarators(declaration):
            yield from GlobalPropertyGenerator(
                declaration=declaration,
                declarator=declarator,
            ).visit(declaration.type)

    def visit_function_definition(self, definition):
        yield
        yield "def call_{name}({parameters}):".format(
            name=definition.name,
            parameters=", ".join(p.declarator.name for p in definition.parameters),
        )
        yield from indent_all(generate_function_body(definition))

    def visit_main_definition(self, definition):
        yield
        yield "def downward_protocol(self):"
        yield from indent_all(generate_downward_protocol_body(self.global_scope, definition.block))


def generate_getter_body(declaration, declarator):
    args = {
        "name": declarator.name,
    }

    yield "if not hasattr(self, '_{name}'):".format(**args)
    yield indent("raise ValueError('not set')")
    yield "return self._{name}".format(**args)


def generate_setter_body(declaration, declarator):
    args = {
        "name": declarator.name,
    }

    yield "if hasattr(self, '_{name}'):".format(**args)
    yield indent("raise ValueError('already set')")
    yield "self._{name} = value".format(**args)


def generate_array_getter_body(declaration, declarator):
    args = {
        "name": declarator.name,
    }

    yield "if not hasattr(self, '_{name}'):".format(**args)
    yield indent("self._{name} = Array()").format(**args)
    yield "return self._{name}".format(**args)


def generate_function_body(definition):
    yield "pass"


def generate_downward_protocol_body(scope, block):
    yield from generate_driver_block(block, scope)
