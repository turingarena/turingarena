import json
import os
import sys


class Submission:
    __slots__ = []

    def __getattr__(self, item):
        return os.environ["SUBMISSION_FILE_" + item.upper()]


def output_data(*data):
    print()
    print(os.environ["EVALUATION_DATA_BEGIN"])
    for d in data:
        print(json.dumps(d))
    print(os.environ["EVALUATION_DATA_END"])
    sys.stdout.flush()
