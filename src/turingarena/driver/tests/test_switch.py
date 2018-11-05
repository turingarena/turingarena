from turingarena.driver.tests.test_utils import define_algorithm

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
            case 3 {
                call res = f3();
                write res;
            }
        }
    }
"""


def test_switch():
    with define_algorithm(
        interface_text=interface_text,
        language_name="C++",
        source_text="""
            int f1() {return 1;}
            int f2() {return 2;}
            int f3() {return 3;}
        """,
    ) as algo:
        with algo.run() as p:
            assert p.functions.f1() == 1
        with algo.run() as p:
            assert p.functions.f2() == 2
        with algo.run() as p:
            assert p.functions.f3() == 3

