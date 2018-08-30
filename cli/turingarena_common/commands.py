from collections import namedtuple

DaemonCommandParameters = namedtuple("DaemonCommandParameters", [
    "log_level",
    "stderr_isatty",
    "command",
])

Pack = namedtuple("Pack", [
    "parts",
    "repositories",
])

GitCloneRepository = namedtuple("GitCloneRepository", [
    "url",
    "branch",
    "depth",
])

WorkingDirectory = namedtuple("WorkingDirectory", [
    "pack",
    "current_directory",
])

EvaluateCommandParameters = namedtuple("EvaluateCommandParameters", [
    "working_directory",
    "file",
    "evaluator",
    "raw_output",
])
