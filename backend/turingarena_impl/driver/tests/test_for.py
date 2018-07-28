from .test_utils import define_algorithm


def test_simple_for():
    with define_algorithm(
        interface_text="""
            function f(n, a[]);
            function g(i);
            
            main {
                read n;
                for i to n {
                    read a[i];
                }
                
                call r = f(n, a);
                write r;
                
                for i to n {
                    call s = g(i);
                    write s;
                }
            }
        """,
        language_name="c++",
        source_text="""
            int *A;
            int f(int n, int a[]) { A = a; return 42; }
            int g(int i) { return A[i]; }
        """,
    ) as algorithm:
        with algorithm.run() as p:
            a = [1, 2, 3, 4, 5, 6, 7, 8]
            assert p.functions.f(len(a), a) == 42
            for i, x in enumerate(a):
                assert p.functions.g(i) == x


def test_double_for():
    with define_algorithm(
            interface_text="""
            function f(n, m, a[][]);
            function g(i, j);

            main {
                read n, m;
                for i to n {
                    for j to m {
                        read a[i][j];
                    }
                }

                call r = f(n, m, a);
                write r;

                for i to n {
                    for j to m {
                        call s = g(i, j);
                        write s;
                    }
                }
            }
        """,
            language_name="c++",
            source_text="""
            int **A;
            int f(int n, int m, int **a) { A = a; return 42; }
            int g(int i, int j) { return A[i][j]; }
        """,
    ) as algorithm:
        with algorithm.run() as p:
            n, m = 3, 4
            a = [[i * j for j in range(m)] for i in range(n)]
            assert p.functions.f(n, m, a) == 42
            for i in range(n):
                for j in range(m):
                    assert p.functions.g(i, j) == i * j