from collections import namedtuple

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

IfConditionResolve = namedtuple("IfConditionResolve", ["node"])
If = namedtuple("If", ["condition", "then_body", "else_body"])

Print = namedtuple("Print", ["arguments"])
Flush = namedtuple("Flush", [])

Read = namedtuple("Read", ["arguments"])
Write = namedtuple("Write", ["arguments"])

Checkpoint = namedtuple("Checkpoint", [])

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

Step = namedtuple("Step", ["direction", "body"])

ParameterDeclaration = namedtuple("ParameterDeclaration", ["variable", "dimensions"])


class Prototype(namedtuple("Prototype", [
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


ConstantDeclaration = namedtuple("ConstantDeclaration", ["variable", "value"])
IntLiteral = namedtuple("IntLiteral", ["value"])
Variable = namedtuple("Variable", ["name"])
Subscript = namedtuple("Subscript", [
    "array",
    "index",
])
Block = namedtuple("Block", ["children"])
Comment = namedtuple("Comment", ["text"])
