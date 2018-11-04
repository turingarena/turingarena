import json
import logging
import os
import random

import sys
import toml

logger = logging.getLogger(__name__)


class InterfaceError(Exception):
    pass


class InterfaceExit(BaseException):
    pass


class AlgorithmError(Exception):
    def __init__(self, process, message, info):
        self.process = process
        self.message = message
        self.info = info


class AlgorithmRuntimeError(AlgorithmError):
    pass


# FIXME: fill-in all arguments when raising the exceptions below
class TimeLimitExceeded(AlgorithmError):
    pass


class MemoryLimitExceeded(AlgorithmError):
    pass


def run_algorithm(source_path, interface_path=None):
    if interface_path is None:
        interface_path = os.path.abspath("interface.txt")

    source_path = os.path.abspath(source_path)

    from turingarena.algorithm import Program
    return Program(
        source_path=source_path,
        language_name=None,
        interface_path=interface_path,
    ).run()


class Submission:
    __slots__ = []

    def __getattr__(self, item):
        return os.environ["SUBMISSION_FILE_" + item.upper()]


submission = Submission()


class Evaluation:
    __slots__ = []

    @staticmethod
    def data(*data):
        print()
        print(os.environ["EVALUATION_DATA_BEGIN"])
        for d in data:
            print(json.dumps(d))
        print(os.environ["EVALUATION_DATA_END"])
        sys.stdout.flush()


evaluation = Evaluation()

try:
    temporary_directory = os.environ["TEMPORARY_DIRECTORY"]
except KeyError:
    pass


try:
    with open("turingarena.toml") as f:
        data = toml.load(f)
except FileNotFoundError:
    data = None

random.seed(os.environ.get("TURINGARENA_SEED", None))
