from collections import deque
from tempfile import TemporaryDirectory
from contextlib import contextmanager

from turingarena.algorithm import Algorithm
from turingarena.interface.exceptions import Diagnostic
from turingarena.interface.interface import InterfaceDefinition
from turingarena.sandbox.languages.language import Language
from turingarena.loader import make_dummy_package

def callback_mock(calls, return_values=None):
    if return_values is not None:
        return_values = deque(return_values)

    def mock(*args):
        calls.append((mock, args))

        if return_values is not None:
            return return_values.popleft()

    return mock


@contextmanager
def define_algorithm(interface_text, source_text, language_name):
    language = Language.from_name(language_name)

    with TemporaryDirectory(dir="/tmp") as tmp_dir:
        mod = make_dummy_package("test", [tmp_dir])
        source_file_name = f"source{language.extension}"
        interface_file_name = "interface.txt"

        with open(f"{tmp_dir}/{interface_file_name}", "w") as f:
            print(interface_text, file=f)

        with open(f"{tmp_dir}/{source_file_name}", "w") as f:
            print(source_text, file=f)

        yield Algorithm(
            source_name=f"test:{source_file_name}",
            interface_name=f"test:{interface_file_name}",
            language_name=language_name,
        )


def define_algorithms(interface_text, sources):
    for language_name, source_text in sources.items():
        with define_algorithm(
                source_text=source_text,
                language_name=language_name,
                interface_text=interface_text,
        ) as impl:
            yield impl


def assert_no_error(text):
    i = InterfaceDefinition.compile(text)
    for m in i.validate():
        print(m.message)
        raise AssertionError


def assert_error(text, error, *args):
    i = InterfaceDefinition.compile(text)
    error = Diagnostic.build_message(error, *args)
    for m in i.validate():
        print(m)
        if m.message == error:
            return
    raise AssertionError


def test_problem_loading():
    with define_algorithm(
        interface_text="""
            function f() -> int;
            main {
                var int res;
                call f() -> res;
                write res;
            }
        """,
        source_text="""
            int f() {return 1;}
        """,
        language_name="c++",
    ) as algo:
        with algo.run() as p:
            assert p.call.f() == 1