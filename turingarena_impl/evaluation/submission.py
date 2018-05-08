from collections import namedtuple
from enum import Enum


class SubmissionFieldType(Enum):
    STRING = "string"
    FILE = "file"


class SubmissionField(namedtuple("SubmissionField", ["type", "value"])):
    pass
