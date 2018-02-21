import logging
import os

from turingarena.sandbox.algorithm import Algorithm
from turingarena.sandbox.cpp import CppAlgorithmSource, ElfAlgorithmExecutable
from turingarena.sandbox.python import PythonAlgorithmSource, PythonAlgorithmExecutableScript

logger = logging.getLogger(__name__)


def load_algorithm_source(filename, *, language=None, **kwargs):
    if language is None:
        lang_by_extensions = {
            "cpp": "c++",
            "py": "python",
        }
        source_extension = filename.split(".")[-1]
        if source_extension not in lang_by_extensions:
            raise ValueError("unable to determine language from file extension")
        language = lang_by_extensions[source_extension]

    source_classes = {
        "c++":    CppAlgorithmSource,
        "python": PythonAlgorithmSource
    }

    if language not in source_classes:
        raise ValueError("unsupported language: {}".format(language))
    cls = source_classes[language]

    with open(filename) as f:
        text = f.read()

    logger.debug(f"source class: {cls}, kwargs: {kwargs}")

    return cls(
        text=text,
        language=language,
        filename=filename,
        **kwargs,
    )


def load_algorithm(algorithm_dir):
    with open(os.path.join(algorithm_dir, "language.txt")) as f:
        language = f.read().strip()

    with open(os.path.join(algorithm_dir, "interface.txt")) as f:
        protocol_name, interface_name = f.read().strip().split(":", 1)

    executable_classes = {
        "c++": ElfAlgorithmExecutable,
        "python": PythonAlgorithmExecutableScript,
    }
    cls = executable_classes[language]

    return Algorithm(
        protocol_name=protocol_name,
        interface_name=interface_name,
        source=None,
        executable=cls(algorithm_dir=algorithm_dir),
    )
