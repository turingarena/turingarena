from collections import namedtuple
from enum import Enum


class ProcessStatus(Enum):
    RUNNING = 0
    TERMINATED_SUCCESSFULLY = 1
    TERMINATED_WITH_ERROR = 2


class SandboxProcessInfo(namedtuple("SandboxProcessInfo", [
    "status",
    "memory_usage",
    "time_usage",
    "error",
])):
    def to_payloads(self):
        return dict(
            status=self.status.name,
            time_usage=str(self.time_usage),
            memory_usage=str(self.memory_usage),
            error=self.error,
        )

    @classmethod
    def from_payloads(cls, payloads):
        return cls(
            status=ProcessStatus[payloads["status"]],
            time_usage=float(payloads["time_usage"]),
            memory_usage=float(payloads["memory_usage"]),
            error=payloads["error"],
        )
