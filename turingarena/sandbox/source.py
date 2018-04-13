import logging
import os
import shutil

from collections import namedtuple

from turingarena.loader import find_package_path, split_module
from turingarena.sandbox.languages.language import Language

logger = logging.getLogger(__name__)


class AlgorithmSource(namedtuple("AlgorithmSource", [
    "interface",
    "language",
    "source_path",
])):
    __slots__ = []

    @staticmethod
    def load(name, *, language=None, interface):
        mod, rel_path = split_module(name)
        source_path = find_package_path(mod, rel_path)

        if language is None:
            base, ext = os.path.splitext(source_path)
            language = Language.from_extension(ext)

        return language.source(
            interface=interface,
            language=language,
            source_path=source_path,
        )

    def compile(self, algorithm_dir):
        logger.info(f"Compiling algorithm source into dir '{algorithm_dir}'")

        os.mkdir(algorithm_dir)
        shutil.copyfile(self.source_path, f"{algorithm_dir}/source{self.language.extension}")

        with open(f"{algorithm_dir}/language.txt", "w") as f:
            print(self.language.name, file=f)

        with open(f"{algorithm_dir}/skeleton{self.language.extension}", "w") as f:
            self.language.skeleton_generator(self.interface).write_to_file(f)

        logger.debug("Starting language-specific compilation")
        self.do_compile(algorithm_dir)

    def do_compile(self, algorithm_dir):
        pass
