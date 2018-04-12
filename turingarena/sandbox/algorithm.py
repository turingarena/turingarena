import os
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena.interface.interface import InterfaceDefinition
from turingarena.sandbox.languages.language import Language
from turingarena.sandbox.source import AlgorithmSource


class CompiledAlgorithm:
    def __init__(self, algorithm_dir, *, interface_name):
        self.algorithm_dir = algorithm_dir
        self.interface_name = interface_name

    @staticmethod
    @contextmanager
    def load(*, source_name, interface_name, language_name):
        language = Language.from_name(language_name)
        interface = InterfaceDefinition.load(interface_name)
        algorithm_source = AlgorithmSource.load(
            source_name,
            interface=interface,
            language=language,
        )

        with TemporaryDirectory(dir="/tmp") as temp_dir:
            algorithm_dir = os.path.join(temp_dir, "algorithm")
            algorithm_source.compile(algorithm_dir)

            yield CompiledAlgorithm(algorithm_dir, interface_name=interface_name)
