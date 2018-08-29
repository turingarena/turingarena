from collections import namedtuple

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
    "evaluator",
])
