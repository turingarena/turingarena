import pytest

from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.test_utils import algorithm

protocol_text = """
    interface simple {
        function run();
        main {
            call run();
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
    with cpp_algorithm("""
            #include <stdio.h>
            
            void run() 
            {
                fopen("name", "r");
            }
    """) as algo:
        with algo.run() as (process, proxy):
            with pytest.raises(AlgorithmRuntimeError) as e:
                proxy.run()
