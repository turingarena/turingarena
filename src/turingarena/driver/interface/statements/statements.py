from turingarena.driver.interface.statements.call import MethodResolveArgumentsNode, MethodCallbacksNode, \
    MethodCallCompletedNode, MethodReturnNode, CallStatement, MethodCallbacksStopNode
from turingarena.driver.interface.statements.callback import ReturnStatement
from turingarena.driver.interface.statements.if_else import ResolveIfNode
from turingarena.driver.interface.statements.io import CheckpointStatement
from turingarena.driver.interface.statements.switch import SwitchResolveNode
from .callback import ExitStatement
from .for_loop import ForStatement
from .if_else import IfStatement
from .io import ReadStatement, WriteStatement
from .loop import LoopStatement, BreakStatement
from .switch import SwitchStatement

statement_classes = {
    "checkpoint": [
        CheckpointStatement,
    ],
    "read": [
        ReadStatement,
    ],
    "write": [
        WriteStatement,
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
        ExitStatement,
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
