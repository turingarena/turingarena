import logging

from turingarena.interfaces.analysis.declaration import process_simple_declaration, \
    process_declarators
from turingarena.interfaces.analysis.expression import compile_expression, compile_range
from turingarena.interfaces.analysis.scope import Scope
from turingarena.interfaces.analysis.types import ScalarType
from turingarena.interfaces.visitor import accept_statement

logger = logging.getLogger(__name__)


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

        for statement in self.block.statements:
            logger.debug("compiling block item {}".format(statement))
            statement.outer_block = block
            accept_statement(statement, visitor=self)

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

    def visit_var_statement(self, statement):
        process_declarators(statement, scope=self.scope)
        self.block.locals.append(statement)

    def compile_arguments(self, statement):
        for e in statement.arguments:
            compile_expression(e, scope=self.scope)

    def visit_statement(self, statement):
        accept_statement(statement, visitor=self)

    def visit_input_statement(self, statement):
        self.compile_arguments(statement)

    def visit_output_statement(self, statement):
        self.compile_arguments(statement)

    def visit_flush_statement(self, statement):
        pass

    def visit_exit_statement(self, statement):
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

        process_simple_declaration(statement.index, scope=new_scope)
        statement.index.type = ScalarType("int")

        compile_block(statement.body, scope=new_scope, parent=self.block)

        self.expect_calls(statement.body.first_calls)

    def visit_if_statement(self, stmt):
        compile_expression(stmt.condition, scope=self.scope)

        new_scope_then = Scope(self.scope)
        compile_block(stmt.then_body, scope=new_scope_then, parent=self.block)
        self.expect_calls(stmt.then_body.first_calls)
        if hasattr(stmt, 'else_body'):
            new_scope_else = Scope(self.scope)
            compile_block(stmt.else_body, scope=new_scope_else, parent=self.block)
            self.expect_calls(stmt.else_body.first_calls)

    def visit_return_statement(self, stmt):
        compile_expression(stmt.value, scope=self.scope)


compile_block = BlockCompiler
