from collections import namedtuple

SandboxProcessInfo = namedtuple("SandboxProcessInfo", [
    "memory_usage",
    "time_usage",
    "error",
])
