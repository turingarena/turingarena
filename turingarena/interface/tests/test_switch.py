from turingarena.algorithm import Algorithm
from turingarena.sandbox.languages.language import Language

interface_text = """
    function f1() -> int;
    function f2() -> int;
    function f3() -> int;
    
    main {
        var int operation;
        read operation;
    
        var int result;
        switch (operation) {
            case 1 {
                call f1() -> result;
            }
            case 2 {
                call f2() -> result;
            }
            default {
                call f3() -> result;
            }
        }
        write result;
    }
"""


def test_switch():
    with Algorithm.load(
        interface_text=interface_text,
        language=Language.from_name("c++"),
        source_text="""
        int f1() {return 1;}
        int f2() {return 2;}
        int f3() {return 3;}
        """,
    ) as algo:
        with algo.run() as p:
            assert p.call.f1() == 1
        with algo.run() as p:
            assert p.call.f2() == 2
        with algo.run() as p:
            assert p.call.f3() == 3

