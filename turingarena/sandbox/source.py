import os
from abc import abstractmethod

from turingarena.common import ImmutableObject
from turingarena.sandbox.algorithm import logger


class AlgorithmSource(ImmutableObject):
    __slots__ = [
        "language",
        "filename",
        "text",
    ]

    def compile(self, *, algorithm_dir, protocol_name, interface_name):
        logger.info(f"Compiling algorithm source {self} into algorithm dir '{algorithm_dir}'")

        logger.debug(f"Creating empty algorithm directory '{algorithm_dir}'")
        os.mkdir(algorithm_dir)

        logger.debug("Creating language.txt file")
        with open(f"{algorithm_dir}/language.txt", "w") as f:
            print(self.language, file=f)

        with open(f"{algorithm_dir}/interface.txt", "w") as f:
            print(f"{protocol_name}:{interface_name}", file=f)

        logger.debug("Starting language-specific compilation")
        return self.do_compile(
            algorithm_dir=algorithm_dir,
            protocol_name=protocol_name,
            interface_name=interface_name,
        )

    @abstractmethod
    def do_compile(self, algorithm_dir):
        pass
