from collections import deque

from turingarena_impl.interface.tests.test_utils import define_algorithms


def callback_mock(calls, return_values=None):
    if return_values is not None:
        return_values = deque(return_values)

    def mock(*args):
        calls.append((mock, args))

        if return_values is not None:
            return return_values.popleft()

    return mock


def test_callback_no_arguments():
    for algo in define_algorithms(
            interface_text="""
                void test(void c());
                main {
                    void c() {}
                    call test(c);
                }
            """,
            sources={
                'c++': """
                    void test(void c()) {
                        c();
                        c();
                    }
                """,
                'python': """if True:                    
                    def test(c):
                        c()
                        c()
                """,
            }
    ):
        with algo.run() as p:
            calls = []
            c = callback_mock(calls)
            p.call.test(lambda: c())

            assert calls == [
                (c, ()),
                (c, ()),
            ]


def test_callback_with_arguments():
    for algo in define_algorithms(
            interface_text="""
                void test(void c(int a, int b));
                
                main {
                    void c(int a, int b) {
                        write a, b;
                    }

                    call test(c);
                }
            """,
            sources={
                'c++': """
                    void test(void c(int a, int b)) {
                        c(1, 2);
                        c(3, 4);
                    }
                """,
                'python': """if True:
                    def test(c):
                        c(1, 2)
                        c(3, 4)
                """,
            },
    ):
        with algo.run() as p:
            calls = []
            c = callback_mock(calls)
            p.call.test(lambda a, b: c(a, b))

            assert calls == [
                (c, (1, 2)),
                (c, (3, 4)),
            ]


def test_callback_return_value():
    for algo in define_algorithms(
            interface_text="""
                void test(int c(int a));
                main {
                    int c(int a) {
                        write a;
                        read b;
                        return b;
                    }

                    call test(c);
                    checkpoint;
                }
            """,
            sources={
                'c++': """
                    #include <cassert>
                    void test(int c(int a)) {
                        assert(c(1) == 2);
                        assert(c(3) == 4);
                    }
                """,
                'python': """if True:
                    def test(c):
                        assert c(1) == 2
                        assert c(3) == 4
                """
            }
    ):
        with algo.run() as p:
            calls = []
            c = callback_mock(calls, [2, 4])
            p.call.test(lambda a: c(a))

            assert calls == [
                (c, (1,)),
                (c, (3,)),
            ]


def test_interface_no_callbacks():
    for algo in define_algorithms(
            interface_text="""
                int test();
                main {
                    call o = test();
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
                int test(void cb());
                main {
                    void cb() {}
                    call o = test(cb);
                    write o;
                }
            """,
            sources={
                'c++': """
                    int test(void cb()) {
                        cb();
                        cb();
                        return 1;
                    }
                """,
                'python': """if True:
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
            assert p.call.test(cb) == 1
            assert calls == [
                (cb, ()),
                (cb, ()),
            ]


def test_interface_multiple_callbacks():
    for algo in define_algorithms(
            interface_text="""
                function test(void cb1(), void cb2()) -> int;
                main {
                    void cb1() {}
                    void cb2() {}
                    call o = test(cb1, cb2);
                    write o;
                }
            """,
            sources={
                'c++': """
                    int test(void cb1, void cb2) {
                        cb1();
                        cb2();
                        cb2();
                        cb1();
                        return 1;
                    }
                """,
                'python': """if True:
                    def test(cb1, cb2):
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
