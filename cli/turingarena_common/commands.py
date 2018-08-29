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

EvaluateCommand = namedtuple("EvaluateCommand", [
    "working_directory",
    "evaluator",
])
