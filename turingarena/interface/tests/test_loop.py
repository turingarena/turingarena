from .test_utils import assert_interface_error, assert_no_interface_errors, define_algorithm
from turingarena.interface.exceptions import Diagnostic


interface_text = """
    function f1() -> int;
    function f2() -> int;

    main {
        loop {
            var int a;
            read a;
            switch a {
                case 1 {
                    var int b;
                    call f1() -> b;
                    write b;
                    flush;
                }
                case 2 {
                    var int b;
                    call f2() -> b;
                    write b;
                    flush;
                } 
                default {
                    break;
                }
            }
        }
    }
"""


def test_loop():
    with define_algorithm(
        interface_text=interface_text,
        language_name="c++",
        source_text="""
            int compute(int a) {return a;}
            int f1() {return 1;}
            int f2() {return 2;}
        """,
    ) as algo:
        with algo.run() as p:
            print ("running process")
            assert p.call.f1() == 1
            print("call f1() ok")
            assert p.call.f2() == 2
            print("call f2() ok")
            assert p.call.f1() == 1
            print("call f1() ok")


def test_correct():
    assert_no_interface_errors("""
        main {
            loop {
                var int a;
                read a;
                switch a {
                    case 1 {
                        write 5;
                        break;
                    }
                    case 2, 3 {
                        write 2, 3;
                        continue;
                    }
                    default {
                        break;
                    }
                }
            }
        }
    """)


def test_unexpected_break():
    assert_interface_error("""
        main {
            break;
        }
    """, Diagnostic.Messages.UNEXPECTED_BREAK)


def test_unexpected_continue():
    assert_interface_error("""
        main {
            continue;
        }
    """, Diagnostic.Messages.UNEXPECTED_CONTINUE)


def test_unreachable_code():
    assert_interface_error("""
        main {
            loop {
                write 1;
                break;
                write 2;
            }
        }
    """, Diagnostic.Messages.UNREACHABLE_CODE)


def test_infinite_loop():
    assert_interface_error("""
        main {
            loop {
                write 4;
            }
        }        
    """, Diagnostic.Messages.INFINITE_LOOP)