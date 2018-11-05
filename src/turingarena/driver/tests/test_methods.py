from turingarena.driver.interface.diagnostics import Diagnostic
from turingarena.driver.tests.test_utils import define_algorithms, assert_interface_error, define_algorithm


def test_method_no_arguments():
    for algo in define_algorithms(
            interface_text="""
                procedure f();
                main {
                    call f();
                    checkpoint;
                }
            """,
            sources={
                'C++': """
                    void f() {
                    }
                """,
                'Python': """if True:
                    def f():
                        pass
                """
            },
    ):
        with algo.run() as p:
            p.procedures.f()
            p.checkpoint()


def test_method_with_arguments():
    for algo in define_algorithms(
            interface_text="""
                procedure f(a, b);
                main {
                    read a, b;
                    call f(a, b);
                    checkpoint;
                }
            """,
            sources={
                'C++': """
                    #include <cassert>
                    void f(int a, int b) {
                        assert(a == 1 && b == 2);
                    }
                """,
                'Python': """if True:
                    def f(a,b):
                        assert a == 1 and b == 2
                """,
            }
    ):
        with algo.run() as p:
            p.procedures.f(1, 2)
            p.checkpoint()


def test_method_return_value():
    for algo in define_algorithms(
            interface_text="""
                function f(a);
                main {
                    read a;
                    call b = f(a);
                    write b;
                }
            """,
            sources={
                'C++': """
                    #include <cassert>
                    int f(int a) {
                        assert(a == 1);
                        return 2;
                    }
                """,
                'Python': """if True:
                    def f(a):
                        assert a == 1
                        return 2
                """,
                # 'javascript': """function f(a, b) { return 2; }""",
            },
    ):
        with algo.run() as p:
            assert p.functions.f(1) == 2


def test_multiple_call_function_no_args():
    with define_algorithm(
            interface_text="""
                function f();

                main {
                    call a = f();
                    call b = f();
                    write a, b;
                }
            """,
            language_name="C++",
            source_text="int i = 0; int f() { return i++; }",
    ) as algo:
        with algo.run() as p:
            for i in range(2):
                assert p.functions.f() == i


def test_multiple_call_function_args():
    with define_algorithm(
            interface_text="""
                function f(x);

                main {
                    read x;
                    call a = f(x);
                    call b = f(x);
                    write a, b;
                }
            """,
            language_name="C++",
            source_text="""
                #include <cassert>
                int i = 0;
                int f(int x) {
                    assert(x == 2);
                    return i++;
                }
            """,
    ) as algo:
        with algo.run() as p:
            for i in range(2):
                assert p.functions.f(2) == i


def test_multiple_call_procedure_no_args():
    with define_algorithm(
            interface_text="""
                procedure p();

                main {
                    call p();
                    call p();
                    checkpoint;
                }
            """,
            language_name="C++",
            source_text="void p() {}",
    ) as algo:
        with algo.run() as p:
            for i in range(2):
                p.procedures.p()
            p.checkpoint()



def test_multiple_call_procedure_args():
    with define_algorithm(
            interface_text="""
                procedure p(x);

                main {
                    read x;
                    call p(x);
                    call p(x);
                    checkpoint;
                }
            """,
            language_name="C++",
            source_text="""
                #include <cassert>
                void p(int x) { assert(x == 1); }
            """,
    ) as algo:
        with algo.run() as p:
            for i in range(2):
                p.procedures.p(1)
            p.checkpoint()


def test_multiple_function_return_value():
    with define_algorithm(
            interface_text="""
            function sum(a, b);
            
            main {
                for i to 10 {
                    read x, y;
                    call ans = sum(x, y);
                    write ans;
                }
            }
            """,
            language_name="C++",
            source_text="""
            int sum(int a, int b) {return a + b;}
        """,
    ) as algo:
        with algo.run() as p:
            for i in range(10):
                assert p.functions.sum(i, i) == 2 * i


def test_callback_accept_scalars():
    assert_interface_error("""
        procedure f() callbacks {
            procedure cb(a[]);
        }

        main {
        }
    """, Diagnostic.Messages.CALLBACK_PARAMETERS_MUST_BE_SCALARS)
