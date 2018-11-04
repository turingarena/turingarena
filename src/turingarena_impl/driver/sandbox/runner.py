from abc import abstractmethod
from collections.__init__ import namedtuple
from typing import ContextManager

from turingarena_impl.driver.sandbox.connection import SandboxProcessConnection


class ProgramRunner(namedtuple("ProgramRunner", [
    "program",
    "language",
    "interface",
    "temp_dir",
])):
    __slots__ = []

    @abstractmethod
    def run_in_process(self) -> ContextManager[SandboxProcessConnection]:
        pass
