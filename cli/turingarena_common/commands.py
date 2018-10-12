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

LocalExecutionParameters.DEFAULT = LocalExecutionParameters(
    git_dir="/run/turingarena/db.git",
)

Pack = namedtuple("Pack", [
    "repository",
    "commit_oid",
])

GitRepository = namedtuple("GitRepository", [
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
    "submission",
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
