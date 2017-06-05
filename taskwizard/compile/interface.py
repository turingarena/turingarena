from taskwizard.compile.block import compile_block
from taskwizard.compile.declaration import compile_declaration
from taskwizard.compile.scope import Scope


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
        compile_declaration(declaration, scope=self.global_scope)

    def visit_function_declaration(self, declaration):
        compile_declaration(declaration, scope=self.global_scope)

    def visit_main_definition(self, definition):
        compile_block(definition.block, scope=self.global_scope)
