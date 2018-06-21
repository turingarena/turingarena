import json
import logging
import os
import sys

from turingarena.algorithm import Algorithm

logger = logging.getLogger(__name__)


class InterfaceError(Exception):
    pass


class InterfaceExit(BaseException):
    pass


class AlgorithmError(Exception):
    pass


class AlgorithmRuntimeError(AlgorithmError):
    pass


class TimeLimitExceeded(AlgorithmError):
    pass


class MemoryLimitExceeded(AlgorithmError):
    pass


def run_algorithm(source_path, interface_name=":interface.txt"):
    return Algorithm(
        source_name=":" + source_path,
        language_name=None,
        interface_name=interface_name,
    ).run()


class Submission:
    __slots__ = []

    def __getattr__(self, item):
        return os.environ["SUBMISSION_FILE_" + item.upper()]


submission = Submission()


class Evaluation:
    __slots__ = []

    def data(self, *data):
        print()
        print(os.environ["EVALUATION_DATA_BEGIN"])
        for d in data:
            print(json.dumps(d))
        print(os.environ["EVALUATION_DATA_END"])
        sys.stdout.flush()


evaluation = Evaluation()
