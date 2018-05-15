import pytest

from turingarena.driver.client import SandboxError
from .test_utils import define_algorithm


def test_sandbox_error():
    with define_algorithm(
            interface_text="""
                procedure test();
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
            language_name="c++",
    ) as algo:
        with pytest.raises(SandboxError):
            with algo.run() as p:
                p.call.test()
