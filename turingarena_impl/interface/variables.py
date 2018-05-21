from collections import namedtuple
from enum import Enum

Variable = namedtuple("Variable", ["name", "dimensions"])
Reference = namedtuple("Reference", ["variable", "index_count"])

ReferenceActionType = Enum("ReferenceActionType", names=["DECLARED", "RESOLVED"])
ReferenceDirection = Enum("ReferenceDirection", names=["DOWNWARD", "UPWARD"])
ReferenceAction = namedtuple("ReferenceAction", ["reference", "direction", "action_type"])

Allocation = namedtuple("Allocation", ["reference", "size"])
