from turingarena_impl.interface.exceptions import Diagnostic
from turingarena_impl.interface.tests.test_utils import define_algorithms, assert_interface_error, define_algorithm


def test_function_no_arguments():
    for algo in define_algorithms(
            interface_text="""
                function f();
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


def test_function_with_arguments():
    for algo in define_algorithms(
            interface_text="""
                function f(int a, int b);
                main {
                    var int a, b;
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


def test_function_return_value():
    for algo in define_algorithms(
            interface_text="""
                function f(int a) -> int;
                main {
                    var int a, b;
                    read a;
                    call f(a) -> b;
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
            function sum(int a, int b) -> int;
            
            main {
                for (i : 10) {
                    var int x, y, ans;
                    read x, y;
                    call sum(x, y) -> ans;
                    write ans;
                    flush;
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


def test_function_returns_scalar():
    assert_interface_error("""
        function f() -> /*!*/ int[] /*!*/ ;
        main {}
    """, Diagnostic.Messages.RETURN_TYPE_MUST_BE_SCALAR)


def test_callback_accept_scalars():
    assert_interface_error("""
        callback f(int a, /*!*/ int[] b /*!*/) {}
        main {}
    """, Diagnostic.Messages.CALLBACK_PARAMETERS_MUST_BE_SCALARS)
