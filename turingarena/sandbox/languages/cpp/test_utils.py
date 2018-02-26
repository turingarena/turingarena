from contextlib import contextmanager

from turingarena.test_utils import define_many

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
    return define_many(
        interface_text=protocol_text,
        sources={"c++": source},
    )
