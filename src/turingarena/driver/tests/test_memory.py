from pytest import raises
from turingarena import TimeLimitExceeded
from turingarena.driver.tests.test_utils import define_algorithm


def my_algo():
    return define_algorithm(
        interface_text="""
            procedure p1(a);
            procedure p2(a);
            main {
                read i;
                call p1(i);
                checkpoint;
                
                read j;
                call p2(j);
                checkpoint;
            }
        """,
        language_name="C++",
        source_text="""
            void p1(int x) {
                int N = 100000000; // 100Mb
                char *p = new char[N];
            
                for(int i = 0; i < N; i++) {
                    p[i] = i;
                }
            
                delete p;            
            }
            
            void p2(int x) {
            }
        """,
    )


def test_peak_memory_usage_section():
    with my_algo() as algo:
        with algo.run() as p:
            with p.section() as s1:
                p.procedures.p1(0)
                p.checkpoint()
            with p.section() as s2:
                p.procedures.p2(0)
                p.checkpoint()

    print(s1.peak_memory_usage, s2.peak_memory_usage)

    assert s1.peak_memory_usage > 100e6
    assert s2.peak_memory_usage < 50e6
