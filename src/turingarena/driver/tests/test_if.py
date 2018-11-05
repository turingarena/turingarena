from turingarena.driver.tests.test_utils import define_algorithm


def test_if_else_calls():
    with define_algorithm(
            interface_text="""
                function f1();
                function f2();

                main {
                    read condition;

                    if condition {
                        call res = f1();
                        write res;
                    } else {
                        call res = f2();
                        write res;
                    }
                }
            """,
            language_name="C++",
            source_text="""
                int f1() {return 1;}
                int f2() {return 2;}
            """,
    ) as algo:
        with algo.run() as p:
            assert p.functions.f1() == 1
        with algo.run() as p:
            assert p.functions.f2() == 2


def test_if_calls():
    with define_algorithm(
            interface_text="""
                function f1();
                function f2();

                main {
                    read condition;

                    if condition {
                        call res = f1();
                        write res;
                    }
                    
                    call res2 = f2();
                    write res2;
                }
            """,
            language_name="C++",
            source_text="""
                int f1() {return 1;}
                int f2() {return 2;}
            """,
    ) as algo:
        with algo.run() as p:
            assert p.functions.f1() == 1
            assert p.functions.f2() == 2
        with algo.run() as p:
            assert p.functions.f2() == 2
