from turingarena.driver.interface.statements.callback import ExitStatement
from .call import MethodResolveArgumentsNode, MethodCallbacksNode, \
    MethodCallCompletedNode, MethodReturnNode, Call, PrintNoCallbacks
from .callback import Return
from .for_loop import For
from .if_else import ResolveIfNode, If
from .io import CheckpointStatement, Read, Write
from .loop import Loop, Break
from .switch import SwitchResolveNode, Switch

statement_classes = {
    "checkpoint": [
        CheckpointStatement,
    ],
    "read": [
        Read,
    ],
    "write": [
        Write,
    ],
    "call": [
        MethodResolveArgumentsNode,
        MethodCallbacksNode,
        MethodCallCompletedNode,
        MethodReturnNode,
        Call,
        PrintNoCallbacks,
    ],
    "return": [
        Return,
    ],
    "exit": [
        ExitStatement,
    ],
    "for": [
        For,
    ],
    "if": [
        ResolveIfNode,
        If,
    ],
    "loop": [
        Loop,
    ],
    "break": [
        Break,
    ],
    "switch": [
        SwitchResolveNode,
        Switch,
    ],
}
