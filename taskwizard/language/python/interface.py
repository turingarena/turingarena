from taskwizard.generation.utils import indent_all
from taskwizard.language.python.protocol import generate_driver_block


class FieldTypeBuilder:

    def build(self, t):
        return t.accept(self)

    def visit_scalar_type(self, t):
        return {
            "int": "int",
            "int64": "int",
        }[t.base]

    def visit_array_type(self, t):
        return "make_array({item_type})".format(
            item_type=self.build(t.item_type),
        )


class SupportInterfaceItemGenerator:

    def visit_global_declaration(self, declaration):
        yield
        for declarator in declaration.declarators:
            yield "Data._fields['{name}'] = {type}".format(
                name=declarator.name,
                type=FieldTypeBuilder().build(declaration.type),
            )

    def visit_function_declaration(self, declaration):
        yield
        yield "def {name}({parameters}):".format(
            name=declaration.declarator.name,
            parameters=", ".join(
                ["self"] +
                [p.declarator.name for p in declaration.parameters]
            ),
        )
        yield from indent_all(generate_function_body(declaration))

    def visit_main_definition(self, definition):
        yield
        yield "def _downward_protocol(self):"
        yield from indent_all(generate_downward_protocol_body(definition.block))


def generate_function_body(declaration):
    yield "self.downward.send(({values}))".format(
        values=", ".join(
            ['"{name}"'.format(name=declaration.declarator.name)] +
            [p.declarator.name for p in declaration.parameters]
        )
    )


def generate_downward_protocol_body(block):
    yield "next_call = yield"
    yield from generate_driver_block(block)
