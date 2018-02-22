from abc import abstractmethod

from turingarena.common import ImmutableObject


class AlgorithmExecutable(ImmutableObject):
    __slots__ = [
        "algorithm_dir",
        "language",
        "interface",
    ]

    @abstractmethod
    def run(self, connection):
        pass
