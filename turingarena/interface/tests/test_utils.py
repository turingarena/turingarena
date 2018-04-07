from collections import deque

from turingarena.algorithm import Algorithm
from turingarena.interface.exceptions import Diagnostic
from turingarena.interface.interface import InterfaceDefinition
from turingarena.sandbox.languages.language import Language


def callback_mock(calls, return_values=None):
    if return_values is not None:
        return_values = deque(return_values)

    def mock(*args):
        calls.append((mock, args))

        if return_values is not None:
            return return_values.popleft()

    return mock


def define_algorithms(interface_text, sources):
    for language_name, source_text in sources.items():
        with Algorithm.load(
                source_text=source_text,
                language=Language.from_name(language_name),
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
