from collections.__init__ import namedtuple

CallbackStart = namedtuple("CallbackStart", ["prototype"])
Return = namedtuple("Return", ["value"])
CallbackEnd = namedtuple("CallbackEnd", [])
Exit = namedtuple("Exit", [])

ForIndex = namedtuple("ForIndex", ["variable", "range"])

For = namedtuple("For", ["index", "body"])

Call = namedtuple("Call", [
    "method",
    "arguments",
    "return_value",
    "callbacks",
])

CallArgumentsResolve = namedtuple("CallArgumentsResolve", ["method", "arguments"])
CallReturn = namedtuple("CallReturn", ["return_value"])
CallCompleted = namedtuple("CallCompleted", [])
AcceptCallbacks = namedtuple("AcceptCallbacks", ["callbacks"])
PrintNoCallbacks = namedtuple("PrintNoCallbacks", [])


class MainExit(Exit):
    pass


IfConditionResolve = namedtuple("IfConditionResolve", ["node"])
If = namedtuple("If", ["condition", "then_body", "else_body"])

Print = namedtuple("Print", ["arguments"])
Flush = namedtuple("Flush", [])

Read = namedtuple("Read", ["arguments"])
Write = namedtuple("Write", ["arguments"])


class Checkpoint(namedtuple("Checkpoint", [])):
    __slots__ = []


class InitialCheckpoint(Checkpoint):
    __slots__ = []


Loop = namedtuple("Loop", ["body"])
Break = namedtuple("Break", [])
Switch = namedtuple("Switch", ["value", "cases"])
Case = namedtuple("Case", ["labels", "body"])
SwitchValueResolve = namedtuple("SwitchValueResolve", ["node"])
CallbackImplementation = namedtuple("CallbackImplementation", [
    "index",
    "prototype",
    "body",
])


class SequenceNode:
    pass


class Step(namedtuple("Step", ["children", "direction"]), SequenceNode):
    __slots__ = []


class ParameterDeclaration(namedtuple("ParameterDeclaration", ["variable", "dimensions"])):
    __slots__ = []


class CallablePrototype(namedtuple("CallablePrototype", [
    "name",
    "parameter_declarations",
    "has_return_value",
    "callbacks",
])):
    __slots__ = []

    @property
    def parameters(self):
        return [
            p.variable
            for p in self.parameter_declarations
        ]

    @property
    def has_callbacks(self):
        return bool(self.callbacks)


class MethodPrototype(CallablePrototype):
    __slots__ = []


class CallbackPrototype(CallablePrototype):
    __slots__ = []


ConstantDeclaration = namedtuple("ConstantDeclaration", ["variable", "value"])


class Expression:
    __slots__ = []


class IntLiteral(namedtuple("IntLiteral", ["value"]), Expression):
    __slots__ = []


class Variable(namedtuple("Variable", ["name"]), Expression):
    __slots__ = []


class Subscript(namedtuple("Subscript", [
    "array",
    "index",
]), Expression):
    __slots__ = []


class Block(namedtuple("Block", ["children"]), SequenceNode):
    __slots__ = []


Comment = namedtuple("Comment", ["text"])

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
        Call,
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
        If,
    ],
    "loop": [
        Loop,
    ],
    "break": [
        Break,
    ],
    "switch": [
        Switch,
    ],
}
