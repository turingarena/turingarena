from enum import Enum


class ExecutionPhase(Enum):
    UPWARD = 1
    REQUEST = 2
    DOWNWARD = 3