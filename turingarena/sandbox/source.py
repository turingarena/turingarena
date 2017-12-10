import os
from abc import abstractmethod

from turingarena.common import ImmutableObject
from turingarena.sandbox.algorithm import logger


class AlgorithmSource(ImmutableObject):
    __slots__ = [
        "language",
        "filename",
        "text",
        "protocol_name",
        "interface_name",
    ]

    def compile(self, *, algorithm_dir):
        logger.info(f"Compiling algorithm source {self} into algorithm dir '{algorithm_dir}'")

        logger.debug(f"Creating empty algorithm directory '{algorithm_dir}'")
        os.mkdir(algorithm_dir)

        logger.debug("Creating language.txt file")
        with open(f"{algorithm_dir}/language.txt", "w") as language_file:
            print(self.language, file=language_file)

        logger.debug("Starting language-specific compilation")
        return self.do_compile(algorithm_dir)

    @abstractmethod
    def do_compile(self, algorithm_dir):
        pass
