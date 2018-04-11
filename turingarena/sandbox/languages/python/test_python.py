from turingarena.algorithm import Algorithm
from turingarena.sandbox.languages import python

interface_text = """
    function test() -> int;
    main {
        var int o;
        call test() -> o;
        write o;
    }
"""


def test_sandbox_smoke():
    with Algorithm.load(
            interface_text=interface_text,
            language=python.language,
            source_text="""if True:
                def test():
                    return 3
            """,
    ) as algo:
        with algo.run() as p:
            assert p.call.test() == 3

# TODO: add more tests for python
