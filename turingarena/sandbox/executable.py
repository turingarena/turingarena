import logging
from abc import abstractmethod
from collections import namedtuple

logger = logging.getLogger(__name__)


class AlgorithmExecutable(namedtuple("AlgorithmExecutable", [
    "algorithm_dir",
    "interface",
    "language",
])):
    __slots__ = []

    @abstractmethod
    def run(self, connection):
        pass
