from turingarena.test_utils import callback_mock, algorithm


def test_interface_no_callbacks():
    protocol_text="""
        interface interface_no_callbacks {
            function test() -> int;
            main {
                var int o;
                call test() -> o;
                output o;
            }
        }
    """
    source_mapping = {
        'c++' : """
            int test() {
                return 1;
            }
        """,
        'python' : """if True:
            def test():
                return 1
        """,
        }

    for lang, source in source_mapping.items():
        with algorithm(
                protocol_text=protocol_text,
                language=lang,
                source_text=source,
                interface_name="interface_no_callbacks",
        ) as impl:
            with impl.run() as (process, p):
                assert p.test() == 1


def test_interface_one_callback():
    protocol_text="""
        interface interface_one_callback {
            callback cb() {}
            function test() -> int;
            main {
                var int o;
                call test() -> o;
                output o;
            }
        }
    """

    source_mapping = {
        'c++' : """
            void cb();
            
            int test() {
                cb();
                cb();
                return 1;
            }
        """,
        'python' : """if True:
            from __main__ import cb
            
            def test():
                cb()
                cb()
                return 1
        """,
        }

    for lang, source in source_mapping.items():
        with algorithm(
                protocol_text=protocol_text,
                language=lang,
                source_text=source,
                interface_name="interface_one_callback",
        ) as impl:
            with impl.run() as (process, p):
                calls = []
                cb = callback_mock(calls)
                assert p.test(cb=cb) == 1
                assert calls == [
                    (cb, ()),
                    (cb, ()),
                ]


def test_interface_multiple_callbacks():
    protocol_text="""
        interface interface_multiple_callbacks {
            callback cb1() {}
            callback cb2() {}
            function test() -> int;
            main {
                var int o;
                call test() -> o;
                output o;
            }
        }
    """
    source_mapping = { 
        'c++':"""
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
        'python' : """if True:
            from __main__ import cb1, cb2
            def test():
                cb1()
                cb2()
                cb2()
                cb1()
                return 1
        """,
        }

    for lang, source in source_mapping.items():
        with algorithm(
                protocol_text=protocol_text,
                language=lang,
                source_text=source,
                interface_name="interface_multiple_callbacks",
        ) as impl:
            with impl.run() as (process, p):
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
