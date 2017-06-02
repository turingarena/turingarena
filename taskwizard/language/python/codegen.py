import os

from taskwizard.generation.codegen import AbstractDriverGenerator, AbstractInterfaceDriverGenerator, AbstractSupportGenerator
from taskwizard.generation.scope import Scope
from taskwizard.generation.utils import write_to_file, indent_all, indent
from taskwizard.grammar import SyntaxVisitor


class SupportInterfaceDeclarationGenerator(SyntaxVisitor):

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
            yield from indent_all(self.generate_getter_body(declaration, declarator))
            yield
            yield "@{name}.setter".format(**args)
            yield "def {name}(self, value):".format(**args)
            yield from indent_all(self.generate_setter_body(declaration, declarator))

    def generate_getter_body(self, declaration, declarator):
        args = {
            "name": declarator.name,
        }

        yield "if self.__{name} is None:".format(**args)
        yield indent("raise ValueError('not set')")
        yield "return self.__{name}".format(**args)

    def generate_setter_body(self, declaration, declarator):
        args = {
            "name": declarator.name,
        }

        yield "if self.__{name} is not None:".format(**args)
        yield indent("raise ValueError('already set')")
        yield "self.__{name} = value".format(**args)

    def visit_function_definition(self, definition):
        return []

    def visit_main_definition(self, definition):
        return []


class InterfaceDriverGenerator(AbstractInterfaceDriverGenerator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.module_path = os.path.join(
            self.driver_generator.package_dir,
            self.interface.name + ".py"
        )

    def generate(self):
        module_file = open(self.module_path, "w")
        write_to_file(self.generate_module(), module_file)

    def generate_module(self):
        global_scope = {}

        yield "class {name}:".format(
            name=self.interface.name
        )
        yield from indent_all(self.generate_class_body())

    def generate_class_body(self):
        generator = SupportInterfaceDeclarationGenerator()
        for item in self.interface.interface_items:
            yield from generator.visit(item)


class DriverGenerator(AbstractDriverGenerator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.package_dir = os.path.join(self.dest_dir, "interfaces")

    def generate(self):
        os.mkdir(self.package_dir)

        for interface in self.task.interfaces:
            self.generate_interface(interface)

    def generate_interface(self, interface):
        InterfaceDriverGenerator(self, interface).generate()


class SupportGenerator(AbstractSupportGenerator):
    pass