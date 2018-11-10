import json
import os
import random
import sys

from turingarena.driver.client.exceptions import *
from turingarena.driver.client.program import Program
from turingarena.goals import Goals
from turingarena.metadata import load_metadata


def run_algorithm(source_path, interface_path=None):
    if interface_path is None:
        interface_path = os.path.abspath("interface.txt")

    source_path = os.path.abspath(source_path)

    return Program(
        source_path=source_path,
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

metadata = load_metadata()
_parameters_dict = metadata.get("parameters", {})


class Parameters:
    def __getitem__(self, item):
        return _parameters_dict[item]

    def __getattr__(self, item):
        return self[item]


parameters = Parameters()

_scoring_metadata = load_metadata().get("scoring", {})
_declared_goals = _scoring_metadata.get("goals", [])

goals = Goals(on_assign_goal=evaluation.data, declared_goals=_declared_goals)

random.seed(os.environ.get("TURINGARENA_SEED", None))
