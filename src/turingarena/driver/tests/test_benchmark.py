from turingarena.driver.tests.test_utils import define_algorithm


def test_benchmark():
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
