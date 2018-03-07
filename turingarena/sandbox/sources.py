import logging

from turingarena.sandbox.languages.cpp.source import CppAlgorithmSource
from turingarena.sandbox.languages.python.source import PythonAlgorithmSource
from turingarena.sandbox.languages.java.source import JavaAlgorithmSource

logger = logging.getLogger(__name__)


def load_source(text, *, language, interface):
    source_classes = {
        "c++": CppAlgorithmSource,
        "python": PythonAlgorithmSource,
        "java": JavaAlgorithmSource
    }
    cls = source_classes[language]
    return cls(
        text=text,
        language=language,
        interface=interface,
    )
