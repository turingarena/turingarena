import logging
import os
from abc import abstractmethod

from turingarena.common import ImmutableObject

logger = logging.getLogger(__name__)


class AlgorithmSource(ImmutableObject):
    __slots__ = [
        "interface",
        "language",
        "filename",
        "text",
    ]

    def compile(self, algorithm_dir):
        logger.info(f"Compiling algorithm source {self} into algorithm dir '{algorithm_dir}'")

        os.mkdir(algorithm_dir)
        with open(f"{algorithm_dir}/language.txt", "w") as f:
            print(self.language, file=f)

        with open(f"{algorithm_dir}/interface.txt", "w") as f:
            print(self.interface, file=f)

        logger.debug("Starting language-specific compilation")
        self.do_compile(algorithm_dir)

    @abstractmethod
    def do_compile(self, algorithm_dir):
        pass
