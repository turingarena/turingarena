import json
from collections import namedtuple


class EvaluationEvent(namedtuple("EvaluationEvent", ["json_data"])):
    def json_line(self):
        return json.dumps(self.json_data)

    def __getattr__(self, item):
        return self.json_data[item]

    def __str__(self):
        return self.json_line()
