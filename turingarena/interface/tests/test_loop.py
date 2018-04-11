from .test_utils import assert_error, assert_no_error
from turingarena.interface.exceptions import Diagnostic


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
