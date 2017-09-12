from turingarena.language.python.compiler.runtimegen.protocol import protocol_generators, global_data_generator

from turingarena.compiler.codegen.utils import indent_all, indent


class InterfaceGenerator:

    def visit_interface_definition(self, interface):
        yield
        yield
        yield "class Interface(BaseInterface):"
        yield from indent_all(self.generate_class_body(interface))
        yield from global_data_generator.generate(interface)
        for phase, generator in protocol_generators.items():
            yield from generator.generate(interface)
        yield
        yield
        yield "def {name}(downward_pipe, upward_pipe, **kwargs):".format(name=interface.name)
        yield from indent_all(self.generate_factory_body(interface))

    def generate_factory_body(self, interface):
        yield "return Interface("
        yield from indent_all(self.generate_factory_args())
        yield ")"

    def generate_factory_args(self):
        for p in [
            "downward_pipe",
            "upward_pipe",
            "upward_data",
            "upward_control",
            "downward_control",
            "downward_data",
            "global_data",
        ]:
            yield "{p}={p},".format(p=p)
        yield "**kwargs"

    def generate_class_body(self, interface):
        for g in interface.variable_declarations:
            yield from g.accept(self)

        for g in interface.function_declarations:
            yield from g.accept(self)

        for g in interface.callback_declarations:
            yield from g.accept(self)

    def visit_variable_declaration(self, declaration):
        yield
        yield "# " + declaration.info()
        for declarator in declaration.declarators:
            yield
            yield "@property"
            yield "def {name}(self):".format(name=declarator.name)
            yield indent("return self._engine.globals.{name}[:]".format(name=declarator.name))
            yield
            yield "@{name}.setter".format(name=declarator.name)
            yield "def {name}(self, value):".format(name=declarator.name)
            yield indent("self._engine.globals.{name}[:] = value".format(name=declarator.name))

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


