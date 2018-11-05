from turingarena.driver.tests.test_utils import define_algorithm


interface_text = """
    function test();
    main {
        call o = test();
        write o;
    }
"""


def test_sandbox_smoke():
    with define_algorithm(
            interface_text=interface_text,
            language_name="Python",
            source_text="""if True:
                def test():
                    return 3
            """,
    ) as algo:
        with algo.run() as p:
            assert p.functions.test() == 3
