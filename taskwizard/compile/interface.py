from taskwizard.compile.block import compile_block
from taskwizard.compile.declaration import compile_declaration
from taskwizard.compile.scope import Scope


class InterfaceCompiler:

    def compile(self, interface):
        interface.variable_declarations = []
        interface.function_declarations = []
        interface.callback_declarations = []
        compiler = InterfaceItemCompiler(interface)
        for item in interface.interface_items:
            item.accept(compiler)


class InterfaceItemCompiler:

    def __init__(self, interface):
        self.interface = interface
        self.global_scope = Scope()

    def visit_variable_declaration(self, declaration):
        compile_declaration(declaration, scope=self.global_scope)
        declaration.is_global = True
        self.interface.variable_declarations.append(declaration)

    def visit_function_declaration(self, declaration):
        compile_declaration(declaration, scope=self.global_scope)
        self.interface.function_declarations.append(declaration)

    def visit_callback_declaration(self, declaration):
        compile_declaration(declaration, scope=self.global_scope)
        self.interface.callback_declarations.append(declaration)

    def visit_main_definition(self, definition):
        compile_block(definition.block, scope=self.global_scope)
