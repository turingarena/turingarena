import pytest

from contextlib import contextmanager
from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.tests.test_utils import define_algorithms, load_algorithm


interface_text = """
    function test() -> int;
    main {
        var int o;
        call test() -> o;
        output o;
    }
"""


@contextmanager
def javascript_algorithm(source):
    return load_algorithm(
        interface_text=interface_text,
        language="javascript",
        source_text=source,
    )


def should_raise(javascript_source):
    with javascript_algorithm(javascript_source) as algo:
        with pytest.raises(AlgorithmRuntimeError):
            with algo.run() as p:
                p.call.test()


def test_javascript():
    with javascript_algorithm("""
        function test() {
                return 3;
            }
    """) as algo:
        with algo.run() as p:
            assert p.call.test() == 3


def test_security():
    should_raise("""
        var fs = require('fs');
    """)


def test_loop():
    should_raise("""
        while (true) {}
    """)


def test_multiple_inputs():
    with load_algorithm(
            interface_text="""
                function f(int a, int b) -> int;
                main {
                    var int a, b, c;
                    input a;
                    input b;
                    call f(a, b) -> c;
                    output c;
                }
            """,
            language="javascript",
            source_text="function f(a, b) { return 1; }"
    ) as algo:
        with algo.run() as process:
            assert process.call.f(2, 5) == 1
