from taskwizard.generation.utils import indent_all
from taskwizard.language.python.protocol import BlockDriverGenerator, PreflightDriverGenerator


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
        yield "def _preflight_protocol(self):"
        yield from indent_all(generate_preflight_protocol_body(definition.block))
        yield
        yield "def _downward_protocol(self):"
        yield from indent_all(generate_downward_protocol_body(definition.block))


def generate_function_body(declaration):
    args = {
        "values": ", ".join(
            ['"{name}"'.format(name=declaration.declarator.name)] +
            [p.declarator.name for p in declaration.parameters]
        )
    }

    yield "self.preflight.send(({values}))".format(**args)
    yield "self.downward.send(({values}))".format(**args)


def generate_downward_protocol_body(block):
    yield "next_call = yield"
    yield from BlockDriverGenerator().generate(block)


def generate_preflight_protocol_body(block):
    yield "next_call = yield"
    yield from PreflightDriverGenerator().generate(block)
