import logging
import os

from turingarena.common import ImmutableObject
from turingarena.interface.skeleton.common import CodeGen

logger = logging.getLogger(__name__)


class AlgorithmSource(ImmutableObject):
    __slots__ = [
        "interface",
        "language",
        "text",
    ]

    @staticmethod
    def load(source_text, *, language, interface):
        from turingarena.sandbox.languages.cpp.source import CppAlgorithmSource
        from turingarena.sandbox.languages.java.source import JavaAlgorithmSource
        from turingarena.sandbox.languages.python.source import PythonAlgorithmSource
        from turingarena.sandbox.languages.javascript.source import JavascriptAlgorithmSource

        return {
            "c++": CppAlgorithmSource,
            "python": PythonAlgorithmSource,
            "java": JavaAlgorithmSource,
            "javascript": JavascriptAlgorithmSource,
        }[language](
            text=source_text,
            language=language,
            interface=interface,
        )

    @property
    def language_extension(self):
        return {
            "javascript": "js",
            "java": "java",
            "python": "py",
            "c++": "cpp",
        }[self.language]

    def compile(self, algorithm_dir):
        logger.info(f"Compiling algorithm source into dir '{algorithm_dir}'")

        os.mkdir(algorithm_dir)
        with open(f"{algorithm_dir}/language.txt", "w") as f:
            print(self.language, file=f)

        with open(f"{algorithm_dir}/interface.txt", "w") as f:
            print(self.interface.source_text, file=f)

        with open(f"{algorithm_dir}/source.{self.language_extension}", "w") as f:
            print(self.text, file=f)

        with open(f"{algorithm_dir}/skeleton.{self.language_extension}", "w") as f:
            CodeGen.get_skeleton_generator(self.language)(self.interface).write_to_file(f)

        logger.debug("Starting language-specific compilation")
        self.do_compile(algorithm_dir)

    def do_compile(self, algorithm_dir):
        pass
