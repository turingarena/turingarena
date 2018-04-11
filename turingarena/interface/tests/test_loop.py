from .test_utils import assert_error, assert_no_error
from turingarena.interface.exceptions import Diagnostic


def test_correct():
    assert_no_error("""
        main {
            loop {
                var int a;
                read a;
                switch (a) {
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
    assert_error("""
        main {
            break;
        }
    """, Diagnostic.Messages.UNEXPECTED_BREAK)


def test_unexpected_continue():
    assert_error("""
        main {
            continue;
        }
    """, Diagnostic.Messages.UNEXPECTED_CONTINUE)


def test_unreachable_code():
    assert_error("""
        main {
            loop {
                write 1;
                break;
                write 2;
            }
        }
    """, Diagnostic.Messages.UNREACHABLE_CODE)


def test_infinite_loop():
    assert_error("""
        main {
            loop {
                write 4;
            }
        }        
    """, Diagnostic.Messages.INFINITE_LOOP)