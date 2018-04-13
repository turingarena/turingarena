import pytest

from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.interface.tests.test_utils import define_algorithm

interface_text = """
    function test() -> int;
    main {
        var int o;
        call test() -> o;
        write o;
    }
"""


def javascript_algorithm(source):
    return define_algorithm(
        interface_text=interface_text,
        language_name="java",
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
        function test() {}
    """)


def test_loop():
    should_raise("""
        while (true) {}
    """)


def test_multiple_reads():
    with Algorithm.load(
            interface_text="""
                function f(int a, int b) -> int;
                main {
                    var int a, b, c;
                    read a;
                    read b;
                    call f(a, b) -> c;
                    write c;
                }
            """,
            language=javascript.language,
            source_text="function f(a, b) { return 1; }"
    ) as algo:
        with algo.run() as process:
            assert process.call.f(2, 5) == 1
