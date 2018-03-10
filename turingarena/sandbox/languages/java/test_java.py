from contextlib import contextmanager

import pytest

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
def java_algorithm(java_source):
    return define_algorithms(
        interface_text=interface_text,
        sources={"java": java_source},
    )


def should_raise(java_source):
    with java_algorithm(java_source) as algo:
        with pytest.raises(AlgorithmRuntimeError):
            with algo.run() as p:
                p.call.test()


def test_java():
    with java_algorithm("""
        public class Solution extends Skeleton {
            public int test() {
                return 3;
            }
        }
    """) as algo:
        with algo.run() as p:
            assert p.call.test() == 3


def test_security():
    should_raise("""
        import java.io.*;
        public class Solution extends Skeleton {
            public int test() {
                try {
                    FileReader f = new FileReader("/dev/null");
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
                return 3;
            }
        }
    """)


def test_compile_failure():
    with pytest.raises(CompilationFailed) as e:
        with java_algorithm(r"""public class D {}""") as algo:
            with algo.run() as p:
                p.call.test()
    print(e.value.compilation_output)
