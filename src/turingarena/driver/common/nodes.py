from collections import namedtuple

# expressions

IntLiteral = namedtuple("IntLiteral", ["value"])
Variable = namedtuple("Variable", ["name"])
Subscript = namedtuple("Subscript", [
    "array",
    "index",
])

# compiled statements

Interface = namedtuple("Interface", [
    "constants",
    "methods",
    "main",
])

Constant = namedtuple("Constant", ["variable", "value"])
Parameter = namedtuple("Parameter", ["variable", "dimensions"])
Prototype = namedtuple("Prototype", [
    "name",
    "parameters",
    "has_return_value",
    "callbacks",
])
Block = namedtuple("Block", ["children"])

Read = namedtuple("Read", ["arguments"])
Write = namedtuple("Write", ["arguments"])
Checkpoint = namedtuple("Checkpoint", [])
Call = namedtuple("Call", [
    "method",
    "arguments",
    "return_value",
    "callbacks",
])
Callback = namedtuple("Callback", [
    "index",
    "prototype",
    "body",
])
Return = namedtuple("Return", ["value"])

For = namedtuple("For", ["index", "body"])
ForIndex = namedtuple("ForIndex", ["variable", "range"])

Loop = namedtuple("Loop", ["body"])

If = namedtuple("If", ["condition", "branches"])
IfBranches = namedtuple("IfBranches", ["then_body", "else_body"])
Break = namedtuple("Break", [])
Switch = namedtuple("Switch", ["value", "cases"])
Case = namedtuple("Case", ["labels", "body"])

Exit = namedtuple("Exit", [])
