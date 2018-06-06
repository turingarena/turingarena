from collections import namedtuple
from enum import Enum

Variable = namedtuple("Variable", ["name", "dimensions"])
Reference = namedtuple("Reference", ["variable", "index_count"])

ReferenceStatus = Enum("ReferenceStatus", names=["DECLARED", "RESOLVED"])
ReferenceDirection = Enum("ReferenceDirection", names=["DOWNWARD", "UPWARD"])
ReferenceAction = namedtuple("ReferenceAction", ["reference", "status"])

Allocation = namedtuple("Allocation", ["reference", "size"])
