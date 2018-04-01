from collections import deque

from turingarena.algorithm import Algorithm
from turingarena.interface.interface import InterfaceDefinition


def callback_mock(calls, return_values=None):
    if return_values is not None:
        return_values = deque(return_values)

    def mock(*args):
        calls.append((mock, args))

        if return_values is not None:
            return return_values.popleft()

    return mock


def define_algorithms(interface_text, sources):
    for language, source in sources.items():
        with Algorithm.load(
                source_text=source,
                language=language,
                interface_text=interface_text,
        ) as impl:
            yield impl


def assert_no_error(text):
    i = InterfaceDefinition.compile(text)
    for m in i.validate():
        print(m.message)
        raise AssertionError


def assert_error(text, error):
    i = InterfaceDefinition.compile(text)
    for m in i.validate():
        print(m)
        if m.message == error:
            return
    raise AssertionError
