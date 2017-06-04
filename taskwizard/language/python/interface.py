from taskwizard.generation.scope import Scope
from taskwizard.generation.utils import indent_all, indent
from taskwizard.grammar import SyntaxVisitor
from taskwizard.language.python.protocol import generate_driver_block


class FieldTypeBuilder(SyntaxVisitor):

    def visit_scalar_type(self, t):
        return {
            "int": "int",
            "int64": "int",
        }[t.base]

    def visit_array_type(self, t):
        return "make_array({item_type})".format(
            item_type=self.visit(t.item_type),
        )


class SupportInterfaceItemGenerator(SyntaxVisitor):

    def __init__(self):
        self.global_scope = Scope()

    def visit_global_declaration(self, declaration):
        yield
        for declarator in self.global_scope.process_declarators(declaration):
            yield "Data._fields['{name}'] = {type}".format(
                name=declarator.name,
                type=FieldTypeBuilder().visit(declaration.type),
            )

    def visit_function_definition(self, definition):
        yield
        yield "def {name}({parameters}):".format(
            name=definition.name,
            parameters=", ".join(
                ["self"] +
                [p.declarator.name for p in definition.parameters]
            ),
        )
        yield from indent_all(generate_function_body(definition))

    def visit_main_definition(self, definition):
        yield
        yield "def _downward_protocol(self):"
        yield from indent_all(generate_downward_protocol_body(self.global_scope, definition.block))


def generate_function_body(definition):
    yield "self.downward.send(({values}))".format(
        values=", ".join(
            ["self." + definition.name] +
            [p.declarator.name for p in definition.parameters]
        )
    )


def generate_downward_protocol_body(scope, block):
    yield "next_call = yield"
    yield from generate_driver_block(block, scope)
