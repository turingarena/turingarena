import os
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from typing import Dict, Generator

from turingarena.algorithm import Algorithm
from turingarena_impl.interface.exceptions import Diagnostic
from turingarena_impl.interface.interface import InterfaceDefinition
from turingarena_impl.sandbox.languages.language import Language


@contextmanager
def define_algorithm(interface_text: str, source_text: str, language_name: str) -> Algorithm:
    language = Language.from_name(language_name)

    with TemporaryDirectory(dir="/tmp") as tmp_dir:
        source_file_name = os.path.join(tmp_dir, f"source{language.extension}")
        interface_file_name = os.path.join(tmp_dir, "interface.txt")

        with open(interface_file_name, "w") as f:
            print(interface_text, file=f)

        with open(source_file_name, "w") as f:
            print(source_text, file=f)

        yield Algorithm(
            source_name=f":{source_file_name}",
            interface_name=f":{interface_file_name}",
            language_name=language_name,
        )


def define_algorithms(interface_text: str, sources: Dict[str, str]) -> Generator[Algorithm, None, None]:
    for language_name, source_text in sources.items():
        with define_algorithm(
                source_text=source_text,
                language_name=language_name,
                interface_text=interface_text,
        ) as impl:
            yield impl


def assert_no_interface_errors(text: str):
    i = InterfaceDefinition.compile(text)
    for m in i.validate():
        print(m.message)
        raise AssertionError


def assert_interface_error(text: str, error: str, *args: str):
    i = InterfaceDefinition.compile(text)
    error = Diagnostic.build_message(error, *args)
    for m in i.validate():
        print(m)
        if m.message == error:
            return
    raise AssertionError
