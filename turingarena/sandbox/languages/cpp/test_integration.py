import pytest

from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.test_utils import algorithm

protocol_text = """
    interface simple {
        function test() -> int;
        main {
            var int o;
            call test() -> o;
            output o;
        }
    }
"""


def cpp_algorithm(source):
    return algorithm(
        protocol_text=protocol_text,
        language="c++",
        source_text=source,
        interface_name="simple",
    )


def test_open():
    with cpp_algorithm(r"""
            #include <stdio.h>
            
            int test() 
            {
                fopen("name", "r");
            }
    """) as algo:
        with pytest.raises(AlgorithmRuntimeError) as e:
            with algo.run() as (process, proxy):
                proxy.test()
        assert "invalid return code" in str(e.value)
