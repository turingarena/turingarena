import json
import logging
import os

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
    return os.environ[f"TURINGARENA_DEFAULT_INTERFACE"]


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


def evaluation_result(**data):
    logger.info(f"evaluation result: {data}")
    path = os.environ[f"result_path"]
    assert path
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


class InterfaceError(Exception):
    pass
