import logging
import os
from collections import namedtuple

from turingarena.loader import find_package_path, split_module
from turingarena.sandbox.languages.language import Language

logger = logging.getLogger(__name__)


class AlgorithmSource(namedtuple("AlgorithmSource", [
    "interface",
    "language",
    "text",
])):
    __slots__ = []

    @staticmethod
    def load(name, *, language=None, interface):
        mod, rel_path = split_module(name)
        source_path = find_package_path(mod, rel_path)

        if language is None:
            base, ext = os.path.splitext(source_path)
            language = Language.from_extension(ext)

        with open(source_path) as f:
            source_text = f.read()

        return language.source(
            interface=interface,
            language=language,
            text=source_text,
        )

    def compile(self, algorithm_dir):
        logger.info(f"Compiling algorithm source into dir '{algorithm_dir}'")

        os.mkdir(algorithm_dir)
        with open(f"{algorithm_dir}/language.txt", "w") as f:
            print(self.language.name, file=f)

        with open(f"{algorithm_dir}/interface.txt", "w") as f:
            print(self.interface.source_text, file=f)

        with open(f"{algorithm_dir}/source{self.language.extension}", "w") as f:
            print(self.text, file=f)

        with open(f"{algorithm_dir}/skeleton{self.language.extension}", "w") as f:
            self.language.skeleton_generator(self.interface).write_to_file(f)

        logger.debug("Starting language-specific compilation")
        self.do_compile(algorithm_dir)

    def do_compile(self, algorithm_dir):
        pass
