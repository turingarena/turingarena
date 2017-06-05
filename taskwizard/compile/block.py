from taskwizard.compile.expression import compile_expression, compile_range
from taskwizard.generation.scope import Scope


def compile_block(block, scope):
    compiler = BlockItemCompiler(Scope(scope))
    for item in block.block_items:
        compiler.compile(item)


class BlockItemCompiler:

    def __init__(self, scope):
        self.scope = scope

    def compile(self, item):
        item.accept(self)

    def visit_local_declaration(self, declaration):
        for declarator in self.scope.process_declarators(declaration):
            pass

    def compile_arguments(self, statement):
        for e in statement.arguments:
            compile_expression(e, scope=self.scope)

    def visit_input_statement(self, statement):
        self.compile_arguments(statement)

    def visit_output_statement(self, statement):
        self.compile_arguments(statement)

    def visit_alloc_statement(self, statement):
        self.compile_arguments(statement)
        compile_range(statement.range, scope=self.scope)

    def visit_call_statement(self, statement):
        for p in statement.parameters:
            compile_expression(p, scope=self.scope)
        if statement.return_value is not None:
            compile_expression(statement.return_value, scope=self.scope)

    def visit_for_statement(self, statement):
        compile_range(statement.index.range, scope=self.scope)

        new_scope = Scope(self.scope)
        new_scope.process_simple_declaration(statement.index)
        compile_block(statement.block, scope=new_scope)


