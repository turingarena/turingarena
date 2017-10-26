import logging

from turingarena.protocol.analysis.expression import compile_expression
from turingarena.protocol.analysis.scope import Scope
from turingarena.protocol.analysis.type_expression import compile_type_expression
from turingarena.protocol.types import scalar

logger = logging.getLogger(__name__)


def compile_var(statement, *, scope):
    compile_type_expression(statement.type_expression)
    statement.type = statement.type_expression.descriptor
    for declarator in statement.declarators:
        scope["var", declarator.name] = statement


def compile_if(statement):
    compile_expression(statement.condition, scope=statement.context.scope)

    compile_block(statement.then_body, scope=statement.context.scope, parent=statement.context)
    then_calls = statement.then_body.first_calls

    if statement.else_body:
        compile_block(statement.else_body, scope=statement.context.scope, parent=statement.context)
        else_calls = statement.else_body.first_calls
    else:
        else_calls = {None}

    expect_calls(statement=statement, calls=(then_calls | else_calls))


def compile_for(statement):
    index = statement.index
    compile_expression(index.range, scope=statement.context.scope)

    new_scope = Scope(statement.context.scope)
    new_scope["var", index.declarator.name] = index

    index.type = scalar(int)

    compile_block(statement.body, scope=new_scope, parent=statement.context)

    expect_calls(statement=statement, calls=statement.body.first_calls)


def compile_call(statement):
    expect_calls(statement=statement, calls={statement.function_name})

    for p in statement.parameters:
        compile_expression(p, scope=statement.context.scope)
    if statement.return_value is not None:
        compile_expression(statement.return_value, scope=statement.context.scope)
    statement.function = statement.context.scope["function", statement.function_name]


def expect_calls(*, statement, calls):
    if statement.context.parent is None:
        return
    if None in statement.context.first_calls:
        statement.context.first_calls.remove(None)
        statement.context.first_calls |= calls


def compile_alloc(statement):
    compile_arguments(statement)
    compile_expression(statement.size, scope=statement.context.scope)


def compile_arguments(statement):
    for e in statement.arguments:
        compile_expression(e, scope=statement.context.scope)


def compile_statement(statement):
    compilers = {
        "var": lambda s: compile_var(s, scope=statement.context.scope),

        "function": compile_function,
        "callback": compile_callback,
        "main": compile_main,

        "input": compile_arguments,
        "output": compile_arguments,
        "alloc": compile_alloc,
        "return": lambda s: compile_expression(s.value, scope=statement.context.scope),
        "call": compile_call,
        "flush": lambda s: None,
        "exit": lambda s: None,
        "if": compile_if,
        "for": compile_for,
        "break": lambda s: None,
        "continue": lambda s: None,
        "loop": NotImplemented,
        "switch": NotImplemented,
    }
    compilers[statement.statement_type](statement)


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
        statement.context = block
        compile_statement(statement)


def compile_main(statement):
    compile_block(statement.body, scope=statement.context.scope, outer_declaration=statement)
    statement.context.scope["main"] = statement


def compile_callback(statement):
    statement.context.scope["callback", statement.declarator.name] = statement
    new_scope = compile_signature(context=statement.context, declarator=statement.declarator)
    compile_block(statement.body, scope=new_scope, outer_declaration=statement)


def compile_function(statement):
    statement.context.scope["function", statement.declarator.name] = statement
    compile_signature(context=statement.context, declarator=statement.declarator)


def compile_signature(*, context, declarator):
    new_scope = Scope(context.scope)
    for p in declarator.parameters:
        new_scope["var", p.declarator.name] = p
        compile_type_expression(p.type_expression)
        p.type = p.type_expression.descriptor
    return new_scope


def compile_interface(interface):
    interface.scope = Scope()

    for statement in interface.statements:
        logger.debug("compiling interface statement {}".format(statement))
        statement.context = interface
        compile_statement(statement)
