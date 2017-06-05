from taskwizard.compile.block import compile_block
from taskwizard.generation.scope import Scope


class InterfaceCompiler:

    def compile(self, interface):
        compiler = InterfaceItemCompiler(interface)
        for item in interface.interface_items:
            item.accept(compiler)


class InterfaceItemCompiler:

    def __init__(self, interface):
        self.interface = interface
        self.global_scope = Scope()

    def visit_global_declaration(self, declaration):
        for declarator in self.global_scope.process_declarators(declaration):
            pass

    def visit_function_declaration(self, declaration):
        self.global_scope.process_simple_declaration(declaration)

    def visit_main_definition(self, definition):
        compile_block(definition.block, scope=self.global_scope)
