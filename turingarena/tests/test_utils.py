from collections import deque

import pytest
import tatsu

from turingarena.algorithm import load_algorithm
from turingarena.interface.exceptions import InterfaceError
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
        with load_algorithm(
                source_text=source,
                language=language,
                interface_text=interface_text,
        ) as impl:
            yield impl


def parse_markers(interface_text):
    return tatsu.parse(
        """
            main = { ->(MARKER|$) }*;
            MARKER = /\s*/ '/*!' name:[/\w+/] '*/' /\s*/ ;
        """,
        interface_text,
        parseinfo=True,
    )


def compilation_fails(interface_text, message):
    markers = parse_markers(interface_text)
    with pytest.raises(InterfaceError) as excinfo:
        InterfaceDefinition.compile(interface_text)
    assert excinfo.value.message == message
    assert_at_markers(excinfo.value, markers)


def assert_at_markers(x, markers):
    start, end = markers
    (px, ps, pe) = map(lambda y: y.parseinfo, (x, start, end))
    assert px.pos == ps.endpos and px.endpos == pe.pos


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