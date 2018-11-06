from pytest import raises

from turingarena import MemoryLimitExceeded
from turingarena.driver.tests.test_utils import define_algorithm


def my_algo():
    return define_algorithm(
        interface_text="""
            procedure p1(a);
            procedure p2(a);
            procedure p3(a);
            main {
                read i1;
                call p1(i1);
                checkpoint;

                read i2;
                call p2(i2);
                checkpoint;

                read i3;
                call p3(i3);
                checkpoint;
            }
        """,
        language_name="C++",
        source_text="""
            char *p;
            void p1(int x) {
                int N = 100000000; // 100Mb
                p = new char[N];

                for(int i = 0; i < N; i++) {
                    p[i] = i;
                }
            }

            void p2(int x) {
                delete p;            
            }
            
            void p3(int x) {
            }
        """,
    )


def test_memory_usage():
    with my_algo() as algo:
        with algo.run() as p:
            with p.section() as s1:
                p.procedures.p1(0)
                p.checkpoint()
            assert s1.peak_memory_usage > 100e6
            m1 = p.current_memory_usage
            assert m1 > 100e6
            with p.section() as s2:
                p.procedures.p2(0)
                p.checkpoint()
            assert s2.peak_memory_usage > 100e6
            m2 = p.current_memory_usage
            assert m2 < 50e6
            with p.section() as s3:
                p.procedures.p3(0)
                p.checkpoint()
            assert s3.peak_memory_usage < 50e6

    print(s1.peak_memory_usage, m1, s2.peak_memory_usage, m2, s3.peak_memory_usage)


def test_memory_limit_all_ok():
    with my_algo() as algo:
        with algo.run(memory_limit=150e6) as p:
            with p.section(memory_limit=150e6):
                p.procedures.p1(0)
                p.checkpoint()
                p.limit_memory(150e6)
                p.procedures.p2(0)
                p.checkpoint()
            p.limit_memory(100e6)
            with p.section(memory_limit=100e6):
                p.procedures.p3(0)
                p.checkpoint()


def test_memory_limit_process_exceeded():
    with my_algo() as algo:
        with raises(MemoryLimitExceeded):
            with algo.run(memory_limit=100e6) as p:
                p.procedures.p1(0)
                p.checkpoint()


def test_memory_limit_section_exceeded():
    with my_algo() as algo:
        with algo.run() as p:
            with raises(MemoryLimitExceeded):
                with p.section(memory_limit=100e6):
                    p.procedures.p1(0)
                    p.checkpoint()


def test_memory_limit_point_exceeded():
    with my_algo() as algo:
        with algo.run() as p:
            with raises(MemoryLimitExceeded):
                p.procedures.p1(0)
                p.checkpoint()
                p.limit_memory(100e6)
