from turingarena.tests.test_utils import assert_error, assert_no_error


def test_missing_local_flush():
    assert_error("""
        main {
            var int a;
            write 5;
            read a;
        }
    """, "missing flush between write and read instructions")


def test_missing_flush_for():
    assert_error("""
        main {
            var int a;
            
            for (i : 5) {
                write 4;
            }
            
            read a;
        }
    """, "missing flush between write and read instructions")


def test_missing_flush_for_2():
    assert_error("""
        main {
            var int a;

            for (i : 5) {
                read a;
                write 4;
            }
        }
    """, "missing flush between write and read instructions")


def test_missing_flush_for_3():
    assert_error("""
        main {
            var int a, b;

            for (i : 5) {
                flush;
                read a;
                write 4;
            }
            read b;
        }
    """, "missing flush between write and read instructions")


def test_for():
    assert_no_error("""
        main {
            var int a;

            for (i : 5) {
                read a;
                write 4;
                flush;
            }
            write 4;
        }
    """)


def test_missing_flush_if():
    assert_error("""
        main {
            var int a, b;
            read a;
            if (a) {
                flush;
            } else {
                write 4;
            }
            
            read b;
        }
    """, "missing flush between write and read instructions")


def test_missing_flush_if_2():
    assert_no_error("""
        main {
            var int a, b;
            read a;
            if (a) {
                flush;
            } else {
                write 4;
                flush;
            }

            read b;
        }
    """)


def test_missing_flush_init():
    assert_error("""
        init {
            write 4;
        }
        
        main {
            var int a;
            read a;
        }
    """, "missing flush between write and read instructions")
