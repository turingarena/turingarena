import json
from collections import namedtuple


class EvaluationEvent(namedtuple("EvaluationEvent", ["json"])):
    @staticmethod
    def from_json(json):
        return EvaluationEvent(json)

    @property
    def type(self):
        return self.json["type"]

    @property
    def payload(self):
        return self.json.get("payload", None) # TODO: remove

    def json_line(self):
        return json.dumps(self.as_json_data())

    def as_json_data(self):
        return self.json

    def __str__(self):
        return self.json_line()
