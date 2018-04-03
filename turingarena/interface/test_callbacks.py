from turingarena.tests.test_utils import callback_mock, define_algorithms, assert_error


def test_callback_no_arguments_cpp():
    for algo in define_algorithms(
            interface_text="""
                callback c() {}
                function test();
                main {
                    call test();
                }
            """,
            sources={
                'c++': """
                    void c();
                    void test() {
                        c();
                        c();
                    }
                """,
                'python': """if True:
                    from skeleton import c
                    
                    def test():
                        c()
                        c()
                """,
            }
    ):
        with algo.run() as p:
            calls = []
            c = callback_mock(calls)
            p.call.test(c=lambda: c())

            assert calls == [
                (c, ()),
                (c, ()),
            ]


def test_callback_with_arguments():
    for algo in define_algorithms(
            interface_text="""
                callback c(int a, int b) {
                    write a, b;
                }
                function test();
                main {
                    call test();
                }
            """,
            sources={
                'c++': """
                    void c(int a, int b);
                    void test() {
                        c(1, 2);
                        c(3, 4);
                    }
                """,
                'python': """if True:
                    from skeleton import c
                    def test():
                        c(1, 2)
                        c(3, 4)
                """,
            },
    ):
        with algo.run() as p:
            calls = []
            c = callback_mock(calls)
            p.call.test(c=lambda a, b: c(a, b))

            assert calls == [
                (c, (1, 2)),
                (c, (3, 4)),
            ]


def test_callback_return_value():
    for algo in define_algorithms(
            interface_text="""
                callback c(int a) -> int {
                    write a;
                    flush;
                    var int b;
                    read b;
                    return b;
                }
                function test();
                main {
                    call test();
                    checkpoint;
                }
            """,
            sources={
                'c++': """
                    #include <cassert>
                    int c(int a);
                    void test() {
                        assert(c(1) == 2);
                        assert(c(3) == 4);
                    }
                """,
                'python': """if True:
                    from skeleton import c
                    def test():
                        assert c(1) == 2
                        assert c(3) == 4
                """
            }
    ):
        with algo.run() as p:
            calls = []
            c = callback_mock(calls, [2, 4])
            p.call.test(c=lambda a: c(a))

            assert calls == [
                (c, (1,)),
                (c, (3,)),
            ]


def test_callback_returns_scalar():
    assert_error("""
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
                    write o;
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
                    write o;
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
                    from skeleton import cb
                    
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
                    write o;
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
                    from skeleton import cb1, cb2
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
