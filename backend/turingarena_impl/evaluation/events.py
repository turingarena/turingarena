import json
from collections import namedtuple
from enum import Enum


class EvaluationEventType(Enum):
    TEXT = "text"
    DATA = "data"


class EvaluationEvent(namedtuple("EvaluationEvent", ["type", "payload"])):
    @staticmethod
    def from_json(json):
        return EvaluationEvent(type=EvaluationEventType(json["type"]), payload=json["payload"])

    def json_line(self):
        return json.dumps(self.as_json_data())

    def as_json_data(self):
        return dict(type=self.type.value, payload=self.payload)

    def __str__(self):
        return self.json_line()
