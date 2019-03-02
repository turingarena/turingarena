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


def send_file(file, *, content_type="text/plain", filename=None, segi_as="auto"):
    assert segi_as in ("path", "content", "auto")
    print()
    print(os.environ["EVALUATION_FILE_BEGIN"])
    print("Content-Type:", content_type)
    if segi_as == "auto":
        if os.path.exists(file):
            segi_as = "path"
        else:
            segi_as = "content"
    print(f"X-SEGI-as: {segi_as}")
    if filename:
        assert ";" not in filename and "\"" not in filename
        print(f"Content-disposition: attachment; filename=\"{filename}\"")
    print()
    print(file)
    print(os.environ["EVALUATION_FILE_END"])
    sys.stdout.flush()
