from abc import abstractmethod
from collections import namedtuple
from typing import ContextManager

from turingarena.driver.sandbox.connection import SandboxProcessConnection


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
