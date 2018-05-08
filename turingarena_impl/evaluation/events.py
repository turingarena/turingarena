import json
from collections import namedtuple
from enum import Enum


class EvaluationEventType(Enum):
    TEXT = "text"
    DATA = "data"


class EvaluationEvent(namedtuple("EvaluationEvent", ["type", "payload"])):
    def json_line(self):
        return json.dumps(dict(type=self.type.value, payload=self.payload))
