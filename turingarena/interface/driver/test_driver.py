import pytest

from turingarena.algorithm import Algorithm
from turingarena.interface.driver.client import SandboxError


def test_sandbox_error():
    with Algorithm.load(
            interface_text="""
                function test();
                main {
                    call test();
                    checkpoint;
                }
            """,
            source_text="""
                #include <cstdlib>
                void test() {
                    exit(0);
                }
            """,
            language="c++",
    ) as algo:
        with pytest.raises(SandboxError):
            with algo.run() as p:
                p.call.test()
