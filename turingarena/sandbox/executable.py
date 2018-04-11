import logging
import os
import signal
from abc import abstractmethod
from collections import namedtuple
from contextlib import contextmanager
from subprocess import TimeoutExpired

from turingarena.sandbox.exceptions import AlgorithmRuntimeError

logger = logging.getLogger(__name__)


class AlgorithmExecutable(namedtuple("AlgorithmExecutable", [
    "algorithm_dir",
    "language",
])):
    __slots__ = []

    @staticmethod
    def load(algorithm_dir):
        from turingarena.sandbox.languages.language import Language

        with open(os.path.join(algorithm_dir, "language.txt")) as f:
            language = Language.from_name(f.read().strip())

        return language.executable(
            algorithm_dir=algorithm_dir,
            language=language,
        )

    @abstractmethod
    def run(self, connection):
        pass
