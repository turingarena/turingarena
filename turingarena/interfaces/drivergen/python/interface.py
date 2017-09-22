from turingarena.interfaces.codegen.utils import indent_all, indent
from turingarena.interfaces.drivergen.python.protocol import global_data_generator, \
    porcelain_generator, plumbing_generator


class InterfaceGenerator:
    def visit_interface_definition(self, interface):
        yield
        yield
        yield "class Engine(BaseDriverEngine):"
        yield from indent_all(self.generate_engine_body(interface))
        yield
        yield
        yield "class Driver(BaseDriver):"
        yield from indent_all(self.generate_driver_body(interface))
        yield
        yield
        yield "{name} = Driver".format(name=interface.name)

    def generate_engine_body(self, interface):
        yield from global_data_generator.generate(interface)
        yield from porcelain_generator.generate(interface)
        yield from plumbing_generator.generate(interface)

    def generate_driver_body(self, interface):
        yield "_engine_class = Engine"
        for item in interface.interface_items:
            yield
            yield "# " + item.info()
            yield from item.accept(self)

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
        yield "pass"

    def visit_main_declaration(self, declaration):
        yield "pass"

    def generate_function_def(self, declaration):
        yield "def {name}({parameters}):".format(
            name=declaration.declarator.name,
            parameters=", ".join(
                ["self"] +
                ["arg_{}".format(p.declarator.name) for p in declaration.parameters] +
                ["**kwargs"]
            ),
        )

    def generate_function_body(self, declaration):
        yield "return self._engine.call({args})".format(
            args=", ".join(
                ['"{name}"'.format(name=declaration.declarator.name)] +
                ["arg_{}".format(p.declarator.name) for p in declaration.parameters] +
                ["has_return={}".format(declaration.return_type is not None)] +
                ["**kwargs"]
            )
        )
