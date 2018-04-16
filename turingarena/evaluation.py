import json
import logging
import os

logger = logging.getLogger(__name__)

from turingarena.algorithm import Algorithm


def submitted_algorithm(name="algorithm", *, interface_name=None):
    problem_name = os.environ[f"problem_name"]
    source_name = os.environ[f"submission_{name}_source"]
    language_name = os.environ[f"submission_{name}_language"]

    if interface_name is None:
        interface_name = problem_name

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
