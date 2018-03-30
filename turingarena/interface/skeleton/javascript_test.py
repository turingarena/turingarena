from turingarena.algorithm import load_algorithm


def test_multiple_inputs():
    with load_algorithm(
            interface_text="""
                function f(int a, int b) -> int;
                main {
                    var int a, b, c;
                    input a;
                    input b;
                    call f(a, b) -> c;
                    output c;
                }
            """,
            language="javascript",
            source_text="function f(a, b) { return 1; }"
    ) as algo:
        with algo.run() as process:
            assert process.call.f(2, 5) == 1
