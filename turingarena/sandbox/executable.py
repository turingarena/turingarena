from abc import abstractmethod

from turingarena.common import ImmutableObject
from turingarena.sandbox.client import SandboxClient


class AlgorithmExecutable(ImmutableObject):
    __slots__ = [
        "algorithm_dir",
        "language",
        "protocol_name",
        "interface_name",
    ]

    @abstractmethod
    def start_os_process(self, connection):
        pass

    def sandbox(self):
        return SandboxClient(algorithm_dir=self.algorithm_dir)
