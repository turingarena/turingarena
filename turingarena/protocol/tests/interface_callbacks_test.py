from turingarena.test_utils import callback_mock, define_many


def test_interface_no_callbacks():
    for algo in define_many(
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
        with algo.run() as (process, p):
            assert p.test() == 1


def test_interface_one_callback():
    for algo in define_many(
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
        with algo.run() as (process, p):
            calls = []
            cb = callback_mock(calls)
            assert p.test(cb=cb) == 1
            assert calls == [
                (cb, ()),
                (cb, ()),
            ]


def test_interface_multiple_callbacks():
    for algo in define_many(
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
        with algo.run() as (process, p):
            calls = []
            cb1 = callback_mock(calls)
            cb2 = callback_mock(calls)
            assert p.test(cb1=cb1, cb2=cb2) == 1
            assert calls == [
                (cb1, ()),
                (cb2, ()),
                (cb2, ()),
                (cb1, ()),
            ]
