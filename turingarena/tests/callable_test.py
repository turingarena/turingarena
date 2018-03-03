from turingarena.tests.test_utils import compilation_fails


def test_callback_returns_scalar():
    compilation_fails("""
        callback f(int a) -> /*!*/ int[] /*!*/ {}  
        main {}
    """, "return type must be a scalar")


def test_function_returns_scalar():
    compilation_fails("""
        function f() -> /*!*/ int[] /*!*/ ;
        main {}
    """, "return type must be a scalar")


def test_callback_accept_scalars():
    compilation_fails("""
        callback f(int a, /*!*/ int[] b /*!*/) {}
        main {}
    """, "callback arguments must be scalars")
