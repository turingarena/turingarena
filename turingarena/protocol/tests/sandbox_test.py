import pytest

from turingarena.protocol.tests.util import cpp_implementation
from turingarena.sandbox.exceptions import AlgorithmError


def test_not_compiling():
    with cpp_implementation(
            protocol_text="""
                interface not_compiling {
                    function test() -> int;
                    main {
                        var int o;
                        call test() -> o;
                        output o;
                    }
                }
            """,
            source_text="""
                <wrong>
            """,
            interface_name="not_compiling",
    ) as impl:
        with pytest.raises(AlgorithmError) as e:
            with impl.run() as p:
                p.test()
        assert "compilation failed" in str(e)
