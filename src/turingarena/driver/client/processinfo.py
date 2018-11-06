from collections import namedtuple

SandboxProcessInfo = namedtuple("SandboxProcessInfo", [
    "time_usage",
    "peak_memory_usage",
    "current_memory_usage",
    "error",
])
