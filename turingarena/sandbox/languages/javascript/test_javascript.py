import pytest

from contextlib import contextmanager
from turingarena.sandbox.exceptions import AlgorithmRuntimeError, CompilationFailed
from turingarena.tests.test_utils import define_algorithms


interface_text = """
    function test() -> int;
    main {
        var int o;
        call test() -> o;
        output o;
    }
"""


@contextmanager
def javascript_algorithm(javascript_source):
    return define_algorithms(
        interface_text=interface_text,
        sources={"javascript": javascript_source},
    )


def should_raise(javascript_source):
    with javascript_algorithm(javascript_source) as algo:
        with pytest.raises(AlgorithmRuntimeError):
            with algo.run() as p:
                p.call.test()


def test_java():
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