from turingarena_impl.driver.interface.diagnostics import Diagnostic
from .test_utils import assert_interface_error, define_algorithm


def test_loop_switch_functions():
    with define_algorithm(
        interface_text="""
        function f1();
        function f2();
    
        main {
            loop {
                read a;
                switch a {
                    case 1 {
                        call b = f1();
                        write b;
                    }
                    case 2 {
                        call b = f2();
                        write b;
                    } 
                    case 3 {
                        break;
                    }
                }
            }
            checkpoint;
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
            assert p.functions.f1() == 1
            p.checkpoint()


def test_loop_switch_procedures():
    with define_algorithm(
            interface_text="""
        procedure p1();
        procedure p2();

        main {
            loop {
                read a;
                switch a {
                    case 1 {
                        call p1();
                    }
                    case 2 {
                        call p2();
                    } 
                    case 3 {
                        break;
                    }
                }
            }
            checkpoint;
        }
        """,
            language_name="C++",
            source_text="""
            int p1() {}
            int p2() {}
        """,
    ) as algo:
        with algo.run() as p:
            p.procedures.p1()
            p.procedures.p2()
            p.procedures.p1()
            p.checkpoint()


def test_loop_and_if_functions():
    with define_algorithm(
        interface_text="""
        function f();
        
        main {
            loop {
                read c;
                if c {
                    call r = f();
                    write r;
                } else {
                    break;
                }
            }
        }
        """,
        language_name="C++",
        source_text="int f() { return 42; }",
    ) as algo:
        with algo.run() as p:
            assert p.functions.f() == 42


def test_loop_and_if_procedures():
    with define_algorithm(
        interface_text="""
            procedure p();
    
            main {
                loop {
                    read c;
                    if c {
                        call p();
                    } else {
                        break;
                    }
                }
            }
            """,
        language_name="C++",
        source_text="void p() {}",
    ) as algo:
        with algo.run() as p:
            p.procedures.p()


def test_unexpected_break():
    assert_interface_error("""
        main {
            break;
        }
    """, Diagnostic.Messages.UNEXPECTED_BREAK)


def test_unreachable_code():
    assert_interface_error("""
        function p();
        main {
            loop {
                call a = p();
                write a;
                break;
                call b = p();
                write b;
            }
        }
    """, Diagnostic.Messages.UNREACHABLE_CODE)


# def test_infinite_loop():
#     assert_interface_error("""
#         main {
#             loop {
#             }
#         }
#     """, Diagnostic.Messages.INFINITE_LOOP)
