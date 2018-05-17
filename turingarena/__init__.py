import json
import logging
import os

from future.moves import sys

logger = logging.getLogger(__name__)


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


def get_default_interface():
    return ":interface.txt"


def submitted_algorithm(name=None, *, interface_name=None):
    if name is None:
        source_field_name = "source"
    else:
        source_field_name = "algorithm_" + name + "_source"
    language_field_name = source_field_name + "_language"

    source_name = ":" + os.environ["SUBMISSION_FILE_" + source_field_name.upper()]
    language_name = os.environ.get("SUBMISSION_VALUE_" + language_field_name.upper(), None)

    if interface_name is None:
        interface_name = get_default_interface()

    from turingarena.algorithm import Algorithm
    return Algorithm(
        interface_name=interface_name,
        source_name=source_name,
        language_name=language_name,
    )


def algorithm(source_name, *, language_name=None, interface_name=None):
    if interface_name is None:
        interface_name = get_default_interface()

    from turingarena.algorithm import Algorithm
    return Algorithm(
        interface_name=interface_name,
        source_name=source_name,
        language_name=language_name,
    )


def evaluation_data(*data):
    print()
    print(os.environ["EVALUATION_DATA_BEGIN"])
    for d in data:
        print(json.dumps(d))
    print(os.environ["EVALUATION_DATA_END"])
    sys.stdout.flush()


def evaluation_result(**data):
    evaluation_data(data)


class InterfaceError(Exception):
    pass
