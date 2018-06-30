from collections import namedtuple

SandboxProcessInfo = namedtuple("SandboxProcessInfo", [
    "status",
    "memory_usage",
    "time_usage",
    "error",
])
