import logging
import os
from collections import namedtuple

logger = logging.getLogger(__name__)


class AlgorithmSource(namedtuple("AlgorithmSource", [
    "interface",
    "language",
    "text",
])):
    __slots__ = []

    @staticmethod
    def load(source_text, *, language, interface):
        return language.source(
            text=source_text,
            language=language,
            interface=interface,
        )

    def compile(self, algorithm_dir):
        logger.info(f"Compiling algorithm source into dir '{algorithm_dir}'")

        os.mkdir(algorithm_dir)
        with open(f"{algorithm_dir}/language.txt", "w") as f:
            print(self.language.name, file=f)

        with open(f"{algorithm_dir}/interface.txt", "w") as f:
            print(self.interface.source_text, file=f)

        with open(f"{algorithm_dir}/source.{self.language.extension}", "w") as f:
            print(self.text, file=f)

        with open(f"{algorithm_dir}/skeleton.{self.language.extension}", "w") as f:
            self.language.skeleton_generator(self.interface).write_to_file(f)

        logger.debug("Starting language-specific compilation")
        self.do_compile(algorithm_dir)

    def do_compile(self, algorithm_dir):
        pass
