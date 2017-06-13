from taskwizard.generation.utils import indent_all
from taskwizard.language.python.expression import build_driver_expression
from taskwizard.language.python.protocol import generate_main_block, generate_callback_block
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
        yield
        yield "def accept_callbacks(self, phase):"
        yield from indent_all(self.generate_accept_callbacks_body(interface))
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
        yield from indent_all(generate_callback_block(declaration))

    def visit_main_definition(self, definition):
        yield
        yield "def main(self, phase):"
        yield from indent_all(generate_main_block(definition))

    def generate_accept_callbacks_body(self, interface):
        if len(interface.callback_declarations) == 0:
            yield "pass"
        else:
            yield from self.generate_accept_callbacks_nonempty_body(interface)

    def generate_accept_callbacks_nonempty_body(self, interface):
        yield "while True:"
        yield from indent_all(self.generate_callbacks_loop(interface))

    def generate_callbacks_loop(self, interface):
        yield "cb = self.get_local(phase)"
        yield "if phase == 'upward': cb.value, = self.read_upward(str,)"
        yield "if cb.value == 'return': break"
        for decl in interface.callback_declarations:
            yield "elif cb.value == '{name}': yield from self.callback_{name}(phase)".format(
                name=decl.declarator.name,
            )
        yield "else: raise ValueError('unexpected callback %s' % cb.value)"
