from turingarena.interfaces.analysis.declaration import compile_declaration
from turingarena.interfaces.analysis.expression import compile_expression, compile_range
from turingarena.interfaces.analysis.scope import Scope


import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger, level=logging.DEBUG)


class BlockCompiler:
    def __init__(
            self,
            block,
            scope,
            parent=None,
            outer_declaration=None,
    ):
        self.block = block
        self.scope = Scope(scope)

        logger.debug("compiling block {}".format(block))

        block.parent = parent

        if parent is None:
            block.outer_declaration = outer_declaration
        else:
            assert outer_declaration is None
            block.outer_declaration = parent.outer_declaration

        block.locals = []
        block.first_calls = None
        """A set containing the names of the possible functions
        that can be called first in this block,
        and possibly None if this block could call no function"""

        if parent is not None:
            block.first_calls = {None}  # at the beginning, no functions are possible

        for item in self.block.block_items:
            logger.debug("compiling block item {}".format(item))
            item.outer_block = block
            item.accept(self)

        if block.parent is not None:
            if len(block.locals) > 0 and None in block.first_calls:
                raise ValueError(
                    "An internal block that declares local variables "
                    "must always do at least one function call")

    def expect_calls(self, calls):
        if self.block.parent is None:
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
        compile_block(statement.body, scope=new_scope, parent=self.block)

        self.expect_calls(statement.body.first_calls)

    def visit_return_statement(self, stmt):
        compile_expression(stmt.value, scope=self.scope)


compile_block = BlockCompiler
