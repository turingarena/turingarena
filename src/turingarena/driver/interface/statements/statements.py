from bidict import bidict

from .call import CallStatement
from .callback import ReturnStatement, ExitStatement
from .for_loop import ForStatement
from .if_else import IfStatement
from .io import CheckpointStatement, ReadStatement, WriteStatement
from .loop import LoopStatement, BreakStatement
from .switch import SwitchStatement

statement_classes = bidict({
    "checkpoint": CheckpointStatement,
    "read": ReadStatement,
    "write": WriteStatement,
    "call": CallStatement,
    "return": ReturnStatement,
    "exit": ExitStatement,
    "for": ForStatement,
    "if": IfStatement,
    "loop": LoopStatement,
    "break": BreakStatement,
    "switch": SwitchStatement,
})


def compile_statement(ast, context):
    return statement_classes[ast.statement_type](ast=ast, context=context)
