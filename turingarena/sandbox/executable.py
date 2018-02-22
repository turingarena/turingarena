from abc import abstractmethod

from turingarena.common import ImmutableObject


class AlgorithmExecutable(ImmutableObject):
    __slots__ = [
        "algorithm_dir",
        "language",
        "interface",
    ]

    @abstractmethod
    def start_os_process(self, connection):
        pass
