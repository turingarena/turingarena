from collections import namedtuple

RemoteCommandParameters = namedtuple("RemoteCommandParameters", [
    "log_level",
    "stderr_isatty",
    "local_execution",
    "command",
])

LocalExecutionParameters = namedtuple("LocalExecutionParameters", [
    "git_dir",
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

FileCommandParameters = namedtuple("FileCommandParameters", [
    "working_directory",
    "command",
])

FileCatCommandParameters = namedtuple("FileCatCommandParameters", [
    "path",
])
