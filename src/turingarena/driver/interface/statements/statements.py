from turingarena.driver.interface.statements.callback import ExitStatementAst
from .call import MethodResolveArgumentsNode, MethodCallbacksNode, \
    MethodCallCompletedNode, MethodReturnNode, CallStatement, MethodCallbacksStopNode
from .callback import ReturnStatement
from .for_loop import ForStatement
from .if_else import ResolveIfNode, IfStatement
from .io import CheckpointStatementAst, ReadStatementAst, WriteStatementAst
from .loop import LoopStatement, BreakStatement
from .switch import SwitchResolveNode, SwitchStatement

statement_classes = {
    "checkpoint": [
        CheckpointStatementAst,
    ],
    "read": [
        ReadStatementAst,
    ],
    "write": [
        WriteStatementAst,
    ],
    "call": [
        MethodResolveArgumentsNode,
        MethodCallbacksNode,
        MethodCallCompletedNode,
        MethodReturnNode,
        CallStatement,
        MethodCallbacksStopNode,
    ],
    "return": [
        ReturnStatement,
    ],
    "exit": [
        ExitStatementAst,
    ],
    "for": [
        ForStatement,
    ],
    "if": [
        ResolveIfNode,
        IfStatement,
    ],
    "loop": [
        LoopStatement,
    ],
    "break": [
        BreakStatement,
    ],
    "switch": [
        SwitchResolveNode,
        SwitchStatement,
    ],
}
