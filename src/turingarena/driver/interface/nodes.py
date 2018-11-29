from abc import abstractmethod
from collections.__init__ import namedtuple

PrintCallbackRequest = namedtuple("PrintCallbackRequest", [])
PrintCallbackIndex = namedtuple("PrintCallbackIndex", ["index", "prototype"])
CallbackStart = namedtuple("CallbackStart", ["prototype"])
Return = namedtuple("Return", ["value"])
CallbackEnd = namedtuple("CallbackEnd", [])
Exit = namedtuple("Exit", [])

ForIndex = namedtuple("ForIndex", ["variable", "range"])


class ControlStructure:
    @property
    def bodies(self):
        return tuple(self._get_bodies())

    @abstractmethod
    def _get_bodies(self):
        pass


class For(namedtuple("For", ["index", "body"]), ControlStructure):
    __slots__ = []

    def _get_bodies(self):
        yield self.body


CallNode = namedtuple("CallNode", [
    "method",
    "arguments",
    "return_value",
    "callbacks",
])


class Call(CallNode):
    __slots__ = []


class CallArgumentsResolve(CallNode):
    __slots__ = []


class CallReturn(CallNode):
    __slots__ = []


class CallCompleted(CallNode):
    __slots__ = []


class AcceptCallbacks(CallNode):
    __slots__ = []


class PrintNoCallbacks(CallNode):
    __slots__ = []


class MainExit(Exit):
    pass


class IfNode(namedtuple("IfNode", ["condition", "then_body", "else_body"])):
    __slots__ = []

    @property
    def branches(self):
        return tuple(
            b
            for b in (self.then_body, self.else_body)
            if b is not None
        )


class IfConditionResolve(IfNode):
    __slots__ = []


class If(ControlStructure, IfNode):
    __slots__ = []

    def _get_bodies(self):
        yield self.then_body
        if self.else_body is not None:
            yield self.else_body


Print = namedtuple("Print", ["arguments"])


class IONode:
    __slots__ = []


class Read(namedtuple("Read", ["arguments"]), IONode):
    __slots__ = []


class Write(namedtuple("Write", ["arguments"]), IONode):
    __slots__ = []


class Checkpoint(namedtuple("Checkpoint", [])):
    __slots__ = []


class InitialCheckpoint(Checkpoint):
    __slots__ = []


class Loop(namedtuple("Loop", ["body"]), ControlStructure):
    __slots__ = []

    def _get_bodies(self):
        yield self.body


Break = namedtuple("Break", [])


class SwitchNode(namedtuple("SwitchNode", ["value", "cases"])):
    __slots__ = []


class Switch(ControlStructure, SwitchNode):
    __slots__ = []

    def _get_bodies(self):
        for c in self.cases:
            yield c.body


Case = namedtuple("Case", ["labels", "body"])


class SwitchValueResolve(SwitchNode):
    __slots__ = []


class CallbackImplementation(namedtuple("CallbackImplementation", [
    "index",
    "prototype",
    "body",
])):
    __slots__ = []

    @property
    def default_body(self):
        fake_ast_body = [
            namedtuple("write", ["statement_type", "arguments"])("write", [
                namedtuple("expression", ["expression_type", "variable_name", "indices"])("reference_subscript", p.name,
                                                                                          "")
                for p in self.prototype.parameters
            ])
        ]
        if self.prototype.has_return_value:
            return_var = namedtuple("expression", ["expression_type", "variable_name", "indices"])(
                "reference_subscript", "_result", "")
            fake_ast_body += [
                namedtuple("read", ["statement_type", "arguments"])("read", [return_var]),
                namedtuple("ret", ["statement_type", "value"])("return", return_var),
            ]
        return namedtuple("body", ["statements"])(fake_ast_body)


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


class Literal(Expression):
    __slots__ = []

    @property
    @abstractmethod
    def value(self):
        pass


class IntLiteral(namedtuple("IntLiteral", ["value"]), Literal):
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
