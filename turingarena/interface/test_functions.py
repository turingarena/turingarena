from turingarena.tests.test_utils import define_algorithms, compilation_fails


def test_function_no_arguments():
    for algo in define_algorithms(
            interface_text="""
                function function_no_arguments();
                main {
                    call function_no_arguments();
                }
            """,
            sources={
                'c++': """
                    void function_no_arguments() {
                    }
                """,
                'python': """if True:
                    def function_no_arguments():
                        pass
                """
            },
    ):
        with algo.run() as p:
            p.call.function_no_arguments()


def test_function_with_arguments():
    for algo in define_algorithms(
            interface_text="""
                function function_with_arguments(int a, int b);
                main {
                    var int a, b;
                    input a, b;
                    call function_with_arguments(a, b);
                }
            """,
            sources={
                'c++': """
                    #include <cassert>
                    void function_with_arguments(int a, int b) {
                        assert(a == 1 && b == 2);
                    }
                """,
                'python': """if True:
                    def function_with_arguments(a,b):
                        assert a == 1 and b == 2
                """,
            }
    ):
        with algo.run() as p:
            p.call.function_with_arguments(1, 2)


def test_function_return_value():
    for algo in define_algorithms(
            interface_text="""
                function function_return_value(int a) -> int;
                main {
                    var int a, b;
                    input a;
                    call function_return_value(a) -> b;
                    output b;
                }
            """,
            sources={
                'c++': """
                    #include <cassert>
                    int function_return_value(int a) {
                        assert(a == 1);
                        return 2;
                    }
                """,
                'python': """if True:
                    def function_return_value(a):
                        assert a == 1
                        return 2
                """,
            },
    ):
        with algo.run() as p:
            assert p.call.function_return_value(1) == 2


def test_function_returns_scalar():
    compilation_fails("""
        function f() -> /*!*/ int[] /*!*/ ;
        main {}
    """, "return type must be a scalar")


def test_callback_accept_scalars():
    compilation_fails("""
        callback f(int a, /*!*/ int[] b /*!*/) {}
        main {}
    """, "callback arguments must be scalars")
