from contextlib import contextmanager

from turingarena.tests.test_utils import define_algorithms

protocol_text = """
    function test() -> int;
    main {
        var int o;
        call test() -> o;
        output o;
    }
"""


@contextmanager
def cpp_algorithm(source):
    return define_algorithms(
        interface_text=protocol_text,
        sources={"c++": source},
    )
