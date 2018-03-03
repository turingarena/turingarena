from turingarena.tests.test_utils import callback_mock, define_algorithms, compilation_fails


def test_callback_no_arguments_cpp():
    for algo in define_algorithms(
            interface_text="""
                callback callback_no_arguments() {}
                function test();
                main {
                    call test();
                }
            """,
            sources={
                'c++': """
                    void callback_no_arguments();
                    void test() {
                        callback_no_arguments();
                        callback_no_arguments();
                    }
                """,
                'python': """if True:
                    from __main__ import callback_no_arguments
                    
                    def test():
                        callback_no_arguments()
                        callback_no_arguments()
                """,
            }
    ):
        with algo.run() as p:
            calls = []
            callback_no_arguments = callback_mock(calls)
            p.call.test(callback_no_arguments=callback_no_arguments)

            assert calls == [
                (callback_no_arguments, ()),
                (callback_no_arguments, ()),
            ]


def test_callback_with_arguments():
    for algo in define_algorithms(
            interface_text="""
                callback callback_with_arguments(int a, int b) {
                    output a, b;
                }
                function test();
                main {
                    call test();
                }
            """,
            sources={
                'c++': """
                    void callback_with_arguments(int a, int b);
                    void test() {
                        callback_with_arguments(1, 2);
                        callback_with_arguments(3, 4);
                    }
                """,
                'python': """if True:
                    from __main__ import callback_with_arguments
                    def test():
                        callback_with_arguments(1, 2)
                        callback_with_arguments(3, 4)
                """,
            },
    ):
        with algo.run() as p:
            calls = []
            callback_with_arguments = callback_mock(calls)
            p.call.test(callback_with_arguments=lambda a, b: callback_with_arguments(a, b))

            assert calls == [
                (callback_with_arguments, (1, 2)),
                (callback_with_arguments, (3, 4)),
            ]


def test_callback_return_value():
    for algo in define_algorithms(
            interface_text="""
                callback callback_return_value(int a) -> int {
                    output a;
                    flush;
                    var int b;
                    input b;
                    return b;
                }
                function test();
                main {
                    call test();
                }
            """,
            sources={
                'c++': """
                    #include <cassert>
                    int callback_return_value(int a);
                    void test() {
                        assert(callback_return_value(1) == 2);
                        assert(callback_return_value(3) == 4);
                    }
                """,
                'python': """if True:
                    from __main__ import callback_return_value
                    def test():
                        assert callback_return_value(1) == 2
                        assert callback_return_value(3) == 4
                """
            }
    ):
        with algo.run() as p:
            calls = []
            callback_return_value = callback_mock(calls, [2, 4])
            p.call.test(callback_return_value=lambda a: callback_return_value(a))

            assert calls == [
                (callback_return_value, (1,)),
                (callback_return_value, (3,)),
            ]


def test_callback_returns_scalar():
    compilation_fails("""
        callback f(int a) -> /*!*/ int[] /*!*/ {}  
        main {}
    """, "return type must be a scalar")


def test_interface_no_callbacks():
    for algo in define_algorithms(
            interface_text="""
                function test() -> int;
                main {
                    var int o;
                    call test() -> o;
                    output o;
                }
            """,
            sources={
                'c++': """
                    int test() {
                        return 1;
                    }
                """,
                'python': """if True:
                    def test():
                        return 1
                """,
            },
    ):
        with algo.run() as p:
            assert p.call.test() == 1


def test_interface_one_callback():
    for algo in define_algorithms(
            interface_text="""
                callback cb() {}
                function test() -> int;
                main {
                    var int o;
                    call test() -> o;
                    output o;
                }
            """,
            sources={
                'c++': """
                    void cb();
                    
                    int test() {
                        cb();
                        cb();
                        return 1;
                    }
                """,
                'python': """if True:
                    from __main__ import cb
                    
                    def test():
                        cb()
                        cb()
                        return 1
                """,
            }
    ):
        with algo.run() as p:
            calls = []
            cb = callback_mock(calls)
            assert p.call.test(cb=cb) == 1
            assert calls == [
                (cb, ()),
                (cb, ()),
            ]


def test_interface_multiple_callbacks():
    for algo in define_algorithms(
            interface_text="""
                callback cb1() {}
                callback cb2() {}
                function test() -> int;
                main {
                    var int o;
                    call test() -> o;
                    output o;
                }
            """,
            sources={
                'c++': """
                    void cb1();
                    void cb2();
                    
                    int test() {
                        cb1();
                        cb2();
                        cb2();
                        cb1();
                        return 1;
                    }
                """,
                'python': """if True:
                    from __main__ import cb1, cb2
                    def test():
                        cb1()
                        cb2()
                        cb2()
                        cb1()
                        return 1
                """,
            },
    ):
        with algo.run() as p:
            calls = []
            cb1 = callback_mock(calls)
            cb2 = callback_mock(calls)
            assert p.call.test(cb1=cb1, cb2=cb2) == 1
            assert calls == [
                (cb1, ()),
                (cb2, ()),
                (cb2, ()),
                (cb1, ()),
            ]
