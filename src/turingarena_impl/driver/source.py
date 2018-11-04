import logging
from abc import abstractmethod
from collections import namedtuple

from turingarena_impl.driver.language import Language
from turingarena_impl.loader import find_package_file

logger = logging.getLogger(__name__)


class AlgorithmSource(namedtuple("AlgorithmSource", [
    "interface",
    "language",
    "source_path",
])):
    __slots__ = []

    @staticmethod
    def load(name, *, language=None, interface):
        source_path = find_package_file(name)
        if language is None:
            language = Language.from_source_path(name)

        return language.source(
            interface=interface,
            language=language,
            source_path=source_path,
        )

    @abstractmethod
    def compile(self, compilation_dir):
        pass

    @abstractmethod
    def create_process(self, compilation_dir, connection):
        pass


class CompilationFailed(Exception):
    pass
