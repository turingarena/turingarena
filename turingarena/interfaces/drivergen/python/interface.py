from turingarena.interfaces.codegen.utils import indent_all, indent
from turingarena.interfaces.drivergen.python.protocol import protocol_generators, global_data_generator


class InterfaceGenerator:
    def visit_interface_definition(self, interface):
        yield
        yield
        yield "class Driver(BaseDriver):"
        yield from indent_all(self.generate_class_body(interface))
        yield
        yield
        yield "{name} = Driver".format(name=interface.name)

    def generate_factory_args(self):
        for p in [
            "upward_data",
            "upward_control",
            "downward_control",
            "downward_data",
            "global_data",
        ]:
            yield "{p}={p},".format(p=p)
        yield "**kwargs"

    def generate_class_body(self, interface):
        for item in interface.interface_items:
            yield
            yield "# " + item.info()
            yield from item.accept(self)
        yield from global_data_generator.generate(interface)
        for phase, generator in protocol_generators.items():
            yield from generator.generate(interface)


    def visit_variable_declaration(self, declaration):
        for i, declarator in enumerate(declaration.declarators):
            if i > 0:
                yield
            yield "@property"
            yield "def {name}(self):".format(name=declarator.name)
            yield indent("return self._engine.globals.{name}[:]".format(name=declarator.name))
            yield
            yield "@{name}.setter".format(name=declarator.name)
            yield "def {name}(self, value):".format(name=declarator.name)
            yield indent("self._engine.globals.{name}[:] = value".format(name=declarator.name))

    def visit_function_declaration(self, declaration):
        yield from self.generate_function_def(declaration)
        yield from indent_all(self.generate_function_body(declaration))

    def visit_callback_declaration(self, declaration):
        yield "@abstractmethod"
        yield from self.generate_function_def(declaration)
        yield indent("pass")

    def visit_main_declaration(self, declaration):
        yield "@abstractmethod"
        yield "def main(self):"
        yield indent("pass")

    def generate_function_def(self, declaration):
        yield "def {name}({parameters}):".format(
            name=declaration.declarator.name,
            parameters=", ".join(
                ["self"] +
                [p.declarator.name for p in declaration.parameters]
            ),
        )

    def generate_function_body(self, declaration):
        yield "return self._engine.call({args})".format(
            args=", ".join(
                ['"{name}"'.format(name=declaration.declarator.name)] +
                [p.declarator.name for p in declaration.parameters]
            )
        )
