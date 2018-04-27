import json
import logging
import os

from turingarena_impl.sandbox.languages.language import Language

logger = logging.getLogger(__name__)


class AlgorithmError(Exception):
    pass


class AlgorithmRuntimeError(AlgorithmError):
    pass


class TimeLimitExceeded(AlgorithmError):
    pass


class MemoryLimitExceeded(AlgorithmError):
    pass


def submitted_algorithm(name="algorithm", *, interface_name=None):
    problem_name = os.environ[f"problem_name"]
    source_name = os.environ[f"submission_{name}_source"]
    language_name = os.environ[f"submission_{name}_language"]

    if interface_name is None:
        interface_name = problem_name

    from turingarena_impl.algorithm import Algorithm
    return Algorithm(
        interface_name=interface_name,
        source_name=source_name,
        language_name=language_name,
    )


def algorithm(source_name, *, language_name=None, interface_name=None):
    problem_name = os.environ[f"problem_name"]
    if interface_name is None:
        interface_name = problem_name
    if language_name is None:
        language_name = Language.from_source_name(source_name).name

    from turingarena_impl.algorithm import Algorithm
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
