import json
import os
import sys


class Submission:
    __slots__ = []

    def __getattr__(self, item):
        return os.environ["SUBMISSION_FILE_" + item.upper()]


def send_data(*data):
    print()
    print(os.environ["EVALUATION_DATA_BEGIN"])
    for d in data:
        print(json.dumps(d))
    print(os.environ["EVALUATION_DATA_END"])
    sys.stdout.flush()


def send_file(path, *, content_type="text/plain", filename=None):
    print()
    print(os.environ["EVALUATION_FILE_BEGIN"])
    print("Content-Type:", content_type)
    if filename:
        assert ";" not in filename and "\"" not in filename
        print(f"Content-disposition: attachment; filename=\"{filename}\"")
    print()
    print(path)
    print(os.environ["EVALUATION_FILE_END"])
    sys.stdout.flush()

