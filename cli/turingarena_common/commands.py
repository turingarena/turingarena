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
    "oid",
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

EvaluateRequest = namedtuple("EvaluateRequest", [
    "submission",
    "working_directory",
    "seed",
])

EvaluateCommandParameters = namedtuple("EvaluateCommandParameters", [
    "evaluate_request",
    "raw_output",
])

FileCommandParameters = namedtuple("FileCommandParameters", [
    "working_directory",
    "command",
])

FileCatCommandParameters = namedtuple("FileCatCommandParameters", [
    "path",
])

InfoCommandParameters = namedtuple("InfoCommandParameters", [
    "what",
])

TestCommandParameters = namedtuple("TestCommandParameters", [
    "pytest_arguments",
    "working_directory",
])


MakeCommandParameters = namedtuple("MakeCommandParameters", [
    "what",
    "language",
    "working_directory",
])
