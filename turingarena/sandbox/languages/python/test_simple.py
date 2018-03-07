from turingarena.interface.algorithm import load_algorithm

interface_text = """
    function test() -> int;
    main {
        var int o;
        call test() -> o;
        output o;
    }
"""


def test_sandbox_smoke():
    with load_algorithm(
            interface_text=interface_text,
            language="python",
            source_text="""if True:
                def test():
                    return 3
            """,
    ) as algo:
        with algo.run() as p:
            assert p.call.test() == 3
