from collections import namedtuple

CloudEvaluateRequest = namedtuple("CloudEvaluateRequest", [
    "submission_id",
    "evaluation_id",
    "working_directory",
    "evaluator",
])

CloudGenerateFilesRequest = namedtuple("CloudGenerateFilesRequest", [
    "working_directory",
])
