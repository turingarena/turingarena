import logging
import os

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


def load_algorithm_executable(algorithm_dir):
    language_filename = os.path.join(algorithm_dir, "language.txt")
    with open(language_filename) as language_file:
        language = language_file.read().strip()

    executable_classes = {
        "c++": ElfAlgorithmExecutable,
        "python": PythonAlgorithmExecutableScript,
    }
    cls = executable_classes[language]

    return cls(algorithm_dir=algorithm_dir)
