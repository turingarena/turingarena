from enum import Enum


class ProcessStatus(Enum):
    RUNNING = 0
    TERMINATED_SUCCESSFULLY = 1
    TERMINATED_WITH_ERROR = 2
