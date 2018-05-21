from turingarena_impl.interface.interface import InterfaceDefinition


# TODO: verify generated instructions

def test_scalar_read():
    interface = InterfaceDefinition.compile("""
        procedure p(a);
        main {
            read a;
            call p(a);
            checkpoint;
        }
    """)
    assert not interface.diagnostics()


def test_scalar_write():
    interface = InterfaceDefinition.compile("""
        function f();
        main {
            call a = f();
            write a;
        }
    """)
    assert not interface.diagnostics()
