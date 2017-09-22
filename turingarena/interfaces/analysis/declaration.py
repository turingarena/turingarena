from turingarena.interfaces.analysis import block
from turingarena.interfaces.analysis.scope import Scope
from turingarena.interfaces.analysis.types import ScalarType


class DeclarationCompiler:
    def __init__(self, scope):
        self.scope = scope

    def compile(self, decl):
        decl.accept(self)

    def process_simple_declaration(self, declaration):
        self.scope[declaration.declarator.name] = declaration

    def process_declarators(self, decl):
        for declarator in decl.declarators:
            self.scope[declarator.name] = decl

    def visit_variable_declaration(self, decl):
        self.process_declarators(decl)

    def visit_index_declaration(self, decl):
        self.process_simple_declaration(decl)
        decl.type = ScalarType("int")

    def visit_parameter_declaration(self, decl):
        self.process_simple_declaration(decl)

    def visit_function_declaration(self, decl):
        self.process_simple_declaration(decl)
        new_scope = Scope(self.scope)
        for p in decl.parameters:
            compile_declaration(p, scope=new_scope)

    def visit_callback_declaration(self, decl):
        self.process_simple_declaration(decl)
        new_scope = Scope(self.scope)
        for p in decl.parameters:
            compile_declaration(p, scope=new_scope)
        block.compile_block(decl.block, context=block.BlockContext(True), scope=new_scope)


def compile_declaration(decl, scope):
    DeclarationCompiler(scope).compile(decl)
