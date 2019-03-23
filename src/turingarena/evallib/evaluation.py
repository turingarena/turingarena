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


def _send_file(payload, content_type, filename, segi_as):
    print()
    print(os.environ["EVALUATION_FILE_BEGIN"])
    print("Content-Type:", content_type)
    if filename:
        assert ";" not in filename and "\"" not in filename
        print(f"Content-disposition: attachment; filename=\"{filename}\"")
    print()
    print(f"X-SEGI-as: {segi_as}")
    print(payload)
    print(os.environ["EVALUATION_FILE_END"])
    sys.stdout.flush()


def send_file(path, *, content_type="text/plain", filename=None):
    _send_file(path, content_type, filename, segi_as="path")


def send_file_content(content, *, content_type="text/plain", filename=None):
    _send_file(content, content_type, filename, segi_as="content")
