import logging

from turingarena.protocol.analysis.declaration import process_simple_declaration, \
    process_declarators
from turingarena.protocol.analysis.expression import compile_expression
from turingarena.protocol.analysis.scope import Scope
from turingarena.protocol.analysis.types import ScalarType

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
            self.compile_statement(statement)

        if block.parent is not None:
            if len(block.locals) > 0 and None in block.first_calls:
                raise ValueError(
                    "An internal block that declares local variables "
                    "must always do at least one function call")

    def compile_statement(self, statement):
        compilers = {
            "var": self.compile_var,
            "input": self.compile_arguments,
            "output": self.compile_arguments,
            "alloc": self.compile_alloc,
            "return": lambda s: compile_expression(s.value, scope=self.scope),
            "call": self.compile_call,
            "flush": lambda s: None,
            "exit": lambda s: None,
            "if": self.compile_if,
            "for": self.compile_for,
            "break": lambda s: None,
            "continue": lambda s: None,
            "loop": NotImplemented,
            "switch": NotImplemented,
        }
        compilers[statement.statement_type](statement)

    def compile_alloc(self, statement):
        self.compile_arguments(statement)
        compile_expression(statement.size, scope=self.scope)

    def expect_calls(self, calls):
        if self.block.parent is None:
            return
        if None in self.block.first_calls:
            self.block.first_calls.remove(None)
            self.block.first_calls |= calls

    def compile_var(self, statement):
        process_declarators(statement, scope=self.scope)
        self.block.locals.append(statement)

    def compile_arguments(self, statement):
        for e in statement.arguments:
            compile_expression(e, scope=self.scope)

    def compile_call(self, statement):
        self.expect_calls({statement.function_name})

        for p in statement.parameters:
            compile_expression(p, scope=self.scope)
        if statement.return_value is not None:
            compile_expression(statement.return_value, scope=self.scope)
        statement.function = self.scope[statement.function_name]

    def compile_for(self, statement):
        compile_expression(statement.index.range, scope=self.scope)

        new_scope = Scope(self.scope)

        process_simple_declaration(statement.index, scope=new_scope)
        statement.index.type = ScalarType("int")

        compile_block(statement.body, scope=new_scope, parent=self.block)

        self.expect_calls(statement.body.first_calls)

    def compile_if(self, stmt):
        compile_expression(stmt.condition, scope=self.scope)

        new_scope_then = Scope(self.scope)
        compile_block(stmt.then_body, scope=new_scope_then, parent=self.block)
        self.expect_calls(stmt.then_body.first_calls)
        if hasattr(stmt, 'else_body'):
            new_scope_else = Scope(self.scope)
            compile_block(stmt.else_body, scope=new_scope_else, parent=self.block)
            self.expect_calls(stmt.else_body.first_calls)


compile_block = BlockCompiler
