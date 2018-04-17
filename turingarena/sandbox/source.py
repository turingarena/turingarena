import logging
from abc import abstractmethod
from collections import namedtuple

from turingarena.loader import find_package_path, split_module
from turingarena.sandbox.languages.language import Language

logger = logging.getLogger(__name__)


class AlgorithmSource(namedtuple("AlgorithmSource", [
    "interface",
    "language",
    "source_path",
])):
    __slots__ = []

    @staticmethod
    def load(name, *, language=None, interface):
        mod, rel_path = split_module(name)
        source_path = find_package_path(mod, rel_path)
        if language is None:
            language = Language.from_source_name(name)

        return language.source(
            interface=interface,
            language=language,
            source_path=source_path,
        )

    @abstractmethod
    def run(self, connection):
        pass
