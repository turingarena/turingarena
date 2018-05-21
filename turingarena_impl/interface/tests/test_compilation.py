from turingarena_impl.interface.interface import InterfaceDefinition


# TODO: verify generated instructions

def test_read_scalar():
    interface = InterfaceDefinition.compile("""
        procedure p(a);
        main {
            read a;
            call p(a);
            checkpoint;
        }
    """)
    assert not interface.diagnostics()


def test_read_array_1():
    interface = InterfaceDefinition.compile("""
        procedure p(a[]);
        main {
            for i to 10 {
                read a[i];
            }
            call p(a);
            checkpoint;
        }
    """)
    assert not interface.diagnostics()


def test_read_array_2():
    interface = InterfaceDefinition.compile("""
        procedure p(a[][]);
        main {
            for i to 10 {
                for j to 10 {
                    read a[i][j];
                }
            }
            call p(a);
            checkpoint;
        }
    """)
    assert not interface.diagnostics()


def test_read_array_pass_slice():
    interface = InterfaceDefinition.compile("""
        procedure p(a[]);
        main {
            for i to 10 {
                for j to 10 {
                    read a[i][j];
                }
                call p(a[i]);
            }
            checkpoint;
        }
    """)
    assert not interface.diagnostics()


def test_write_scalar():
    interface = InterfaceDefinition.compile("""
        function f();
        main {
            call a = f();
            write a;
        }
    """)
    assert not interface.diagnostics()


def test_write_array_1():
    interface = InterfaceDefinition.compile("""
        function f();
        main {
            for i to 10 {
                call a[i] = f();
                write a[i];
            }
        }
    """)
    assert not interface.diagnostics()
