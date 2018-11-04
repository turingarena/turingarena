from collections import namedtuple

CloudEvaluateRequest = namedtuple("CloudEvaluateRequest", [
    "evaluation_id",
    "evaluate_request",
])

CloudGenerateFileRequest = namedtuple("CloudGenerateFileRequest", [
    "file_id",
    "working_directory",
])
