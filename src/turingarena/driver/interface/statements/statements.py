from turingarena.driver.interface.statements.callback import Exit
from .call import CallArgumentsResolve, AcceptCallbacks, \
    CallCompleted, CallReturn, Call, PrintNoCallbacks
from .callback import Return
from .for_loop import For
from .if_else import IfConditionResolve, If
from .io import Checkpoint, Read, Write
from .loop import Loop, Break
from .switch import SwitchValueResolve, Switch

statement_classes = {
    "checkpoint": [
        Checkpoint,
    ],
    "read": [
        Read,
    ],
    "write": [
        Write,
    ],
    "call": [
        CallArgumentsResolve,
        AcceptCallbacks,
        CallCompleted,
        CallReturn,
        Call,
        PrintNoCallbacks,
    ],
    "return": [
        Return,
    ],
    "exit": [
        Exit,
    ],
    "for": [
        For,
    ],
    "if": [
        IfConditionResolve,
        If,
    ],
    "loop": [
        Loop,
    ],
    "break": [
        Break,
    ],
    "switch": [
        SwitchValueResolve,
        Switch,
    ],
}
