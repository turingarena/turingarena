from collections import namedtuple
from enum import Enum

Step = namedtuple("Step", ["phases", "body"])
RequestLookahead = namedtuple("RequestLookahead", [])
CallbackStart = namedtuple("CallbackStart", ["prototype"])
CallbackEnd = namedtuple("CallbackEnd", [])
CallArgumentsResolve = namedtuple("CallArgumentsResolve", ["method", "arguments"])
CallReturn = namedtuple("CallReturn", ["return_value"])
CallCompleted = namedtuple("CallCompleted", [])
AcceptCallbacks = namedtuple("AcceptCallbacks", ["callbacks"])
ValueResolve = namedtuple("ValueResolve", ["value", "map"])


class ExecutionPhase(Enum):
    UPWARD = 1
    REQUEST = 2
    DOWNWARD = 3