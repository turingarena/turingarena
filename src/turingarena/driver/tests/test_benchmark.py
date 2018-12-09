from turingarena.driver.tests.test_utils import define_algorithm


def test_single_call():
    with define_algorithm(
            interface_text="""
                procedure p(n, a[]);

                main {
                    read n;
                    for i to n {
                        read a[i];
                    }
                    call p(n, a);
                }
            """,
            language_name="C++",
            source_text="void p(int, int[]) {}",
    ) as algo:
        N = 100000
        print(f"Sending an array of {N} elements...")
        with algo.run() as p:
            p.procedures.p(N, [0] * N)


def test_multiple_calls():
    with define_algorithm(
            interface_text="""
                procedure p(x);

                main {
                    read n;
                    call p(n);
                    for i to n {
                        read a;
                        call p(a);
                    }
                }
            """,
            language_name="C++",
            source_text="void p(int) {}",
    ) as algo:
        N = 10000
        print(f"Sending an array of {N} elements...")
        with algo.run() as p:
            p.procedures.p(N)
            for i in range(N):
                p.procedures.p(0)
