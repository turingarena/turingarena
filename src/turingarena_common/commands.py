from collections import namedtuple

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
