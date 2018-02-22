from contextlib import contextmanager

import pytest

from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.test_utils import define_many

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


@contextmanager
def cpp_algorithm(source):
    return define_many(
        protocol_text=protocol_text,
        interface_name="simple",
        sources={"c++": source},
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
