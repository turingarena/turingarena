from taskwizard.generation.scope import Scope
from taskwizard.generation.utils import indent_all, indent
from taskwizard.grammar import SyntaxVisitor
from taskwizard.language.python.protocol import generate_driver_block


class SupportInterfaceItemGenerator(SyntaxVisitor):

    def __init__(self):
        self.global_scope = Scope()

    def visit_global_declaration(self, declaration):
        for declarator in self.global_scope.process_declarators(declaration):
            args = {
                "name": declarator.name,
            }

            yield
            yield "@property"
            yield "def {name}(self, value):".format(**args)
            yield from indent_all(generate_getter_body(declaration, declarator))
            yield
            yield "@{name}.setter".format(**args)
            yield "def {name}(self, value):".format(**args)
            yield from indent_all(generate_setter_body(declaration, declarator))

    def visit_function_definition(self, definition):
        yield
        yield "def call_{name}({parameters}):".format(
            name=definition.name,
            parameters=", ".join(p.declarator.name for p in definition.parameters),
        )
        yield from indent_all(generate_function_body(definition))

    def visit_main_definition(self, definition):
        yield
        yield "def downward_protocol():"
        yield from indent_all(generate_downward_protocol_body(self.global_scope, definition.block))


def generate_getter_body(declaration, declarator):
    args = {
        "name": declarator.name,
    }

    yield "if self.__{name} is None:".format(**args)
    yield indent("raise ValueError('not set')")
    yield "return self.__{name}".format(**args)


def generate_setter_body(declaration, declarator):
    args = {
        "name": declarator.name,
    }

    yield "if self.__{name} is not None:".format(**args)
    yield indent("raise ValueError('already set')")
    yield "self.__{name} = value".format(**args)


def generate_function_body(definition):
    yield "pass"


def generate_downward_protocol_body(scope, block):
    yield from generate_driver_block(block, scope)
