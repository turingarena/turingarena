from turingarena_impl.interface.diagnostics import Diagnostic
from turingarena_impl.interface.tests.test_utils import define_algorithms, assert_interface_error, define_algorithm


def test_method_no_arguments():
    for algo in define_algorithms(
            interface_text="""
                procedure f();
                main {
                    call f();
                    checkpoint;
                }
            """,
            sources={
                'c++': """
                    void f() {
                    }
                """,
                'python': """if True:
                    def f():
                        pass
                """
            },
    ):
        with algo.run() as p:
            p.call.f()


def test_method_with_arguments():
    for algo in define_algorithms(
            interface_text="""
                procedure f(a, b);
                main {
                    read a, b;
                    call f(a, b);
                    checkpoint;
                }
            """,
            sources={
                'c++': """
                    #include <cassert>
                    void f(int a, int b) {
                        assert(a == 1 && b == 2);
                    }
                """,
                'python': """if True:
                    def f(a,b):
                        assert a == 1 and b == 2
                """,
            }
    ):
        with algo.run() as p:
            p.call.f(1, 2)


def test_method_return_value():
    for algo in define_algorithms(
            interface_text="""
                function f(a);
                main {
                    read a;
                    call b = f(a);
                    write b;
                }
            """,
            sources={
                'c++': """
                    #include <cassert>
                    int f(int a) {
                        assert(a == 1);
                        return 2;
                    }
                """,
                'python': """if True:
                    def f(a):
                        assert a == 1
                        return 2
                """,
                #'javascript': """function f(a, b) { return 2; }""",
            },
    ):
        with algo.run() as p:
            assert p.call.f(1) == 2


def test_multiple_function_return_value():
    with define_algorithm(
        interface_text="""
            function sum(a, b);
            
            main {
                for i to 10 {
                    read x, y;
                    call ans = sum(x, y);
                    write ans;
                }
            }
            """,
        language_name="c++",
        source_text="""
            int sum(int a, int b) {return a + b;}
        """,
    ) as algo:
        with algo.run() as p:
            for i in range(10):
                assert p.call.sum(i, i) == 2*i


def test_callback_accept_scalars():
    assert_interface_error("""
        procedure f() callbacks {
            procedure cb(a[]);
        }

        main {
        }
    """, Diagnostic.Messages.CALLBACK_PARAMETERS_MUST_BE_SCALARS)
