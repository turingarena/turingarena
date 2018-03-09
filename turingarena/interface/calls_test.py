from turingarena.tests.test_utils import compilation_fails


def test_call_non_existing():
    compilation_fails("""
        function f();
        main {
            /*!*/ call g(); /*!*/
        }
    """, "function does not exist")


def test_call_extra_arguments():
    compilation_fails("""
        function f();
        main {
            /*!*/ call f(0, 1); /*!*/
        }
    """, "function f expects 0 argument(s), got 2")


def test_call_missing_arguments():
    compilation_fails("""
        function f(int a, int b);
        main {
            /*!*/ call f(0); /*!*/
        }
    """, "function f expects 2 argument(s), got 1")


def test_call_argument_wrong_type():
    compilation_fails("""
        function f(int[] a);
        main {
            call f(/*!*/ 0 /*!*/);
        }
    """, "argument a of function f: expected int[], got int")


def test_call_missing_return_expression():
    compilation_fails("""
        function f() -> int;
        main {
            /*!*/ call f(); /*!*/
        }
    """, "function f returns int, but no return expression given")


def test_call_extra_return_expression():
    compilation_fails("""
        function f();
        main {
            var int a;
            call f() -> /*!*/ a /*!*/;
        }
    """, "function f does not return a value")


def test_call_return_expression_wrong_type():
    compilation_fails("""
        function f() -> int;
        main {
            var int[] a;
            call f() -> /*!*/ a /*!*/;
        }
    """, "function f returns int, but return expression is int[]")
