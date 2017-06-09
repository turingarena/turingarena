from taskwizard.generation.utils import indent_all
from taskwizard.language.python.protocol import DriverBlockGenerator
from taskwizard.language.python.types import TypeBuilder


class InterfaceGenerator:

    def visit_interface_definition(self, interface):
        yield "class {name}(BaseInterface):".format(
            name=interface.name
        )
        yield from indent_all(self.generate_class_body(interface))

    def generate_class_body(self, interface):
        yield
        yield "_fields = {}"

        for g in interface.variable_declarations:
            yield from g.accept(self)

        for g in interface.function_declarations:
            yield from g.accept(self)

        for g in interface.callback_declarations:
            yield from g.accept(self)

        yield from interface.accept(InterfaceEngineGenerator())

    def visit_variable_declaration(self, declaration):
        yield
        for declarator in declaration.declarators:
            yield "_fields['{name}'] = {type}".format(
                name=declarator.name,
                type=TypeBuilder().build(declaration.type),
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
        yield from indent_all(self.generate_function_body(declaration))

    def visit_callback_declaration(self, declaration):
        yield from []

    def generate_function_body(self, declaration):
        yield "return self._engine.call({args})".format(
            args=", ".join(
                ['"{name}"'.format(name=declaration.declarator.name)] +
                [p.declarator.name for p in declaration.parameters]
            )
        )


class InterfaceEngineGenerator:

    def visit_interface_definition(self, interface):
        yield
        yield "class Engine(BaseInterfaceEngine):"
        yield from indent_all(self.generate_class_body(interface))

    def generate_class_body(self, interface):
        for item in interface.interface_items:
            yield from item.accept(self)

    def visit_variable_declaration(self, declaration):
        yield from []

    def visit_function_declaration(self, declaration):
        yield from []

    def visit_callback_declaration(self, declaration):
        name = declaration.declarator.name
        yield
        yield "def callback_{name}(self, phase):".format(name=name)
        yield from indent_all(DriverBlockGenerator().generate(declaration.block))

    def visit_main_definition(self, definition):
        yield
        yield "def main(self, phase):"
        yield from indent_all(DriverBlockGenerator().generate(definition.block))
