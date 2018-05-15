from turingarena_impl.interface.tests.test_utils import define_algorithm

interface_text = """
    function f1();
    function f2();
    function f3();
    
    main {
        read operation;
    
        switch operation {
            case 1 {
                call res = f1();
                write res;
            }
            case 2 {
                call res = f2();
                write res;
            }
            default {
                call res = f3();
                write res;
            }
        }
    }
"""


def test_switch():
    with define_algorithm(
        interface_text=interface_text,
        language_name="c++",
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

