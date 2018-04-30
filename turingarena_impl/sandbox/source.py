import logging
from abc import abstractmethod
from collections import namedtuple

from turingarena_impl.loader import find_package_path
from turingarena_impl.sandbox.languages.language import Language

logger = logging.getLogger(__name__)


class AlgorithmSource(namedtuple("AlgorithmSource", [
    "interface",
    "language",
    "source_path",
])):
    __slots__ = []

    @staticmethod
    def load(name, *, language=None, interface):
        source_path = find_package_path(name)
        if language is None:
            language = Language.from_source_name(name)

        return language.source(
            interface=interface,
            language=language,
            source_path=source_path,
        )

    @abstractmethod
    def compile(self, compilation_dir):
        pass

    @abstractmethod
    def run(self, compilation_dir, connection):
        pass


class CompilationFailed(Exception):
    pass
