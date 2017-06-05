from taskwizard.compile.declaration import compile_declaration
from taskwizard.compile.expression import compile_expression, compile_range
from taskwizard.compile.scope import Scope


def compile_block(block, scope):
    compiler = BlockItemCompiler(Scope(scope))
    for item in block.block_items:
        compiler.compile(item)
    block.expected_calls = find_expected_calls(block)


class BlockItemCompiler:

    def __init__(self, scope):
        self.scope = scope

    def compile(self, item):
        item.accept(self)

    def visit_local_declaration(self, declaration):
        compile_declaration(declaration, scope=self.scope)

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
        statement.function_declaration = self.scope[statement.function_name]

    def visit_for_statement(self, statement):
        compile_range(statement.index.range, scope=self.scope)

        new_scope = Scope(self.scope)
        compile_declaration(statement.index, scope=new_scope)
        compile_block(statement.block, scope=new_scope)


def find_expected_calls(block):
    for item in block.block_items:
        calls = item.accept(ExpectedCallFinder())
        if calls is not None:
            return calls
    return None


class ExpectedCallFinder:

    def visit_default(self, stmt):
        return None

    def visit_call_statement(self, stmt):
        return set(stmt.function_name)

    def visit_for_statement(self, stmt):
        return find_expected_calls(stmt.block)
