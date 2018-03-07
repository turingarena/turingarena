import logging
import os

from turingarena.protocol.model.model import InterfaceDefinition
from turingarena.sandbox.languages.cpp.executable import ElfAlgorithmExecutable
from turingarena.sandbox.languages.python.executable import PythonAlgorithmExecutableScript

logger = logging.getLogger(__name__)


def load_executable(algorithm_dir):
    with open(os.path.join(algorithm_dir, "language.txt")) as f:
        language = f.read().strip()

    with open(os.path.join(algorithm_dir, "interface.txt")) as f:
        interface_text = f.read()
    interface = InterfaceDefinition.compile(interface_text)

    executable_classes = {
        "c++": ElfAlgorithmExecutable,
        "python": PythonAlgorithmExecutableScript,
    }
    cls = executable_classes[language]

    return cls(
        algorithm_dir=algorithm_dir,
        language=language,
        interface=interface,
    )
