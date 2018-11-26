from collections import namedtuple
from enum import Enum


class Variable(namedtuple("Variable", ["name", "dimensions"])):
    __slots__ = []

    def as_reference(self):
        return Reference(self, index_count=0)


Reference = namedtuple("Reference", ["variable", "index_count"])

ReferenceStatus = Enum("ReferenceStatus", names=["DECLARED", "RESOLVED"])
ReferenceDirection = Enum("ReferenceDirection", names=["DOWNWARD", "UPWARD"])


ReferenceDeclaration = namedtuple("ReferenceAction", ["variable"])
ReferenceResolution = namedtuple("ReferenceAction", ["variable"])


class ReferenceAction(namedtuple("ReferenceAction", ["reference", "status"])):
    def __init__(self, *args, **kwargs):
        super().__init__()

        assert self.reference is not None


VariableDeclaration = namedtuple("VariableDeclaration", ["variable"])
VariableAllocation = namedtuple("VariableAllocation", ["variable", "indexes", "size"])
