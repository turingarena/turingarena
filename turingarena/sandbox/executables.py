import logging
import os

from turingarena.sandbox.languages.cpp import ElfAlgorithmExecutable
from turingarena.sandbox.languages.python import PythonAlgorithmExecutableScript

logger = logging.getLogger(__name__)


def load_executable(algorithm_dir):
    with open(os.path.join(algorithm_dir, "language.txt")) as f:
        language = f.read().strip()

    with open(os.path.join(algorithm_dir, "interface.txt")) as f:
        protocol_name, interface_name = f.read().strip().split(":", 1)

    executable_classes = {
        "c++": ElfAlgorithmExecutable,
        "python": PythonAlgorithmExecutableScript,
    }
    cls = executable_classes[language]

    return cls(
        algorithm_dir=algorithm_dir,
        language=language,
        protocol_name=protocol_name,
        interface_name=interface_name,
    )
