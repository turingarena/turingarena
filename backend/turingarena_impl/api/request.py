from collections import namedtuple

CloudEvaluateRequest = namedtuple("CloudEvaluateRequest", [
    "evaluation_id",
    "evaluate_request",
])

CloudGenerateFileRequest = namedtuple("CloudGenerateFileRequest", [
    "working_directory",
])
