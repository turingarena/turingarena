import logging

from turingarena.protocol.analysis.expression import compile_expression
from turingarena.protocol.analysis.scope import Scope
from turingarena.protocol.analysis.types import compile_type_expression
from turingarena.protocol.types import scalar

logger = logging.getLogger(__name__)


def compile_var(statement, *, scope):
    compile_type_expression(statement.type_expression)
    statement.type = statement.type_expression.descriptor
    for declarator in statement.declarators:
        scope["var", declarator.name] = statement


class BlockStatementCompiler:
    def __init__(self, block):
        self.block = block

    def compile_statement(self, statement):
        compilers = {
            "var": lambda s: compile_var(s, scope=self.block.scope),
            "input": self.compile_arguments,
            "output": self.compile_arguments,
            "alloc": self.compile_alloc,
            "return": lambda s: compile_expression(s.value, scope=self.block.scope),
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
        compile_expression(statement.size, scope=self.block.scope)

    def expect_calls(self, calls):
        if self.block.parent is None:
            return
        if None in self.block.first_calls:
            self.block.first_calls.remove(None)
            self.block.first_calls |= calls

    def compile_arguments(self, statement):
        for e in statement.arguments:
            compile_expression(e, scope=self.block.scope)

    def compile_call(self, statement):
        self.expect_calls({statement.function_name})

        for p in statement.parameters:
            compile_expression(p, scope=self.block.scope)
        if statement.return_value is not None:
            compile_expression(statement.return_value, scope=self.block.scope)
        statement.function = self.block.scope["function", statement.function_name]

    def compile_for(self, statement):
        index = statement.index
        compile_expression(index.range, scope=self.block.scope)

        new_scope = Scope(self.block.scope)
        new_scope["var", index.declarator.name] = index

        index.type = scalar(int)

        compile_block(statement.body, scope=new_scope, parent=self.block)

        self.expect_calls(statement.body.first_calls)

    def compile_if(self, stmt):
        compile_expression(stmt.condition, scope=self.block.scope)

        compile_block(stmt.then_body, scope=self.block.scope, parent=self.block)
        then_calls = stmt.then_body.first_calls

        if stmt.else_body:
            compile_block(stmt.else_body, scope=self.block.scope, parent=self.block)
            else_calls = stmt.else_body.first_calls
        else:
            else_calls = {None}

        self.expect_calls(then_calls | else_calls)


def compile_block(block, scope, parent=None, outer_declaration=None):
    logger.debug("compiling block {}".format(block))

    block.scope = Scope(scope)
    block.parent = parent

    if parent is None:
        block.outer_declaration = outer_declaration
    else:
        assert outer_declaration is None
        block.outer_declaration = parent.outer_declaration

    block.first_calls = None
    """A set containing the names of the possible functions
    that can be called first in this block,
    and possibly None if this block could call no function"""

    if parent is not None:
        block.first_calls = {None}  # at the beginning, no functions are possible

    for statement in block.statements:
        logger.debug("compiling block statement {}".format(statement))
        statement.outer_block = block
        compiler = BlockStatementCompiler(block)
        compiler.compile_statement(statement)

    if block.parent is not None:
        if len(block.scope.locals()) > 0 and None in block.first_calls:
            raise ValueError(
                "An internal block that declares local variables "
                "must always do at least one function call")


class InterfaceStatementCompiler:
    def __init__(self, interface):
        self.interface = interface

    def compile_var(self, statement):
        compile_var(statement, scope=self.interface.scope)

    def compile_function(self, statement):
        self.interface.scope["function", statement.declarator.name] = statement
        self.compile_signature(statement)

    def compile_callback(self, statement):
        self.interface.scope["callback", statement.declarator.name] = statement
        new_scope = self.compile_signature(statement)
        compile_block(statement.body, scope=new_scope, outer_declaration=statement)

    def compile_signature(self, statement):
        new_scope = Scope(self.interface.scope)
        for p in statement.declarator.parameters:
            new_scope["var", p.declarator.name] = p
            compile_type_expression(p.type_expression)
            p.type = p.type_expression.descriptor
        return new_scope

    def compile_main(self, statement):
        compile_block(statement.body, scope=self.interface.scope, outer_declaration=statement)
        self.interface.scope["main"] = statement


def compile_interface(interface):
    interface.scope = Scope()

    compiler = InterfaceStatementCompiler(interface)

    for statement in interface.statements:
        statement.interface = interface
        logger.debug("compiling interface statement {}".format(statement))
        getattr(compiler, "compile_" + statement.statement_type)(statement)
