from turingarena.interfaces.analysis.declaration import compile_declaration
from turingarena.interfaces.analysis.expression import compile_expression, compile_range
from turingarena.interfaces.analysis.scope import Scope


class BlockContext:
    def __init__(self, root=False):
        self.root = root


def compile_block(block, context, scope):
    block.context = context
    compiler = BlockCompiler(block, scope)
    compiler.compile()


class BlockCompiler:
    def __init__(self, block, scope):
        self.block = block
        self.scope = Scope(scope)

        self.block.locals = []
        self.block.first_calls = None
        """A set containing the names of the possible functions
        that can be called first in this block,
        and possibly None if this block could call no function"""

        if not self.block.context.root:
            self.block.first_calls = {None}  # at the beginning, no functions are possible

    def compile(self):
        for item in self.block.block_items:
            item.accept(self)
        if True \
                and not self.block.context.root \
                and len(self.block.locals) > 0 \
                and None in self.block.first_calls:
            raise ValueError(
                "An internal block that declares local variables "
                "must always do at least one function call")

    def expect_calls(self, calls):
        if self.block.context.root:
            return
        if None in self.block.first_calls:
            self.block.first_calls.remove(None)
            self.block.first_calls |= calls

    def visit_variable_declaration(self, declaration):
        compile_declaration(declaration, scope=self.scope)
        self.block.locals.append(declaration)

    def compile_arguments(self, statement):
        for e in statement.arguments:
            compile_expression(e, scope=self.scope)

    def visit_input_statement(self, statement):
        self.compile_arguments(statement)

    def visit_output_statement(self, statement):
        self.compile_arguments(statement)

    def visit_flush_statement(self, statement):
        pass

    def visit_alloc_statement(self, statement):
        self.compile_arguments(statement)
        compile_range(statement.range, scope=self.scope)

    def visit_call_statement(self, statement):
        self.expect_calls({statement.function_name})

        for p in statement.parameters:
            compile_expression(p, scope=self.scope)
        if statement.return_value is not None:
            compile_expression(statement.return_value, scope=self.scope)
        statement.function_declaration = self.scope[statement.function_name]

    def visit_for_statement(self, statement):
        compile_range(statement.index.range, scope=self.scope)

        new_scope = Scope(self.scope)
        compile_declaration(statement.index, scope=new_scope)
        compile_block(statement.block, context=BlockContext(), scope=new_scope)

        self.expect_calls(statement.block.first_calls)

    def visit_return_statement(self, stmt):
        if stmt.expression is not None:
            compile_expression(stmt.expression, scope=self.scope)
