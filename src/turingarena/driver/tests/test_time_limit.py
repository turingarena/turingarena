from pytest import raises, approx

from turingarena import TimeLimitExceeded
from turingarena.driver.tests.test_utils import define_algorithm


def my_algo():
    return define_algorithm(
        interface_text="""
            procedure fast(a);
            procedure slow(a);
            main {
                read i;
                call fast(i);
                checkpoint;
                
                read j;
                call slow(j);
                checkpoint;
            }
        """,
        language_name="Python",
        source_text="""if True:
            def fast(x):
                pass

            def slow(x):
                for i in range(1000000):
                    pass
        """,
    )


def test_time_usage():
    with my_algo() as algo:
        with algo.run() as p:
            with p.section() as fast:
                p.procedures.fast(0)
                p.checkpoint()
            with p.section() as slow:
                p.procedures.slow(0)
                p.checkpoint()
    assert 0.0 < fast.time_usage < 0.001
    assert 0.005 < slow.time_usage < 1.0
    assert p.time_usage == approx(fast.time_usage + slow.time_usage)


def test_time_limit_passed():
    with my_algo() as algo:
        with algo.run(time_limit=1.0) as p:
            with p.section(time_limit=0.001):
                p.procedures.fast(0)
                p.checkpoint()
            with p.section(time_limit=1.0):
                p.procedures.slow(0)
                p.checkpoint()


def test_time_limit_section_exceeded():
    with my_algo() as algo:
        with algo.run() as p:
            with p.section(time_limit=0.001):
                p.procedures.fast(0)
                p.checkpoint()
            with raises(TimeLimitExceeded):
                with p.section(time_limit=0.001):
                    p.procedures.slow(0)
                    p.checkpoint()


def test_time_limit_process_exceeded():
    with my_algo() as algo:
        with raises(TimeLimitExceeded):
            with algo.run(time_limit=0.001) as p:
                p.procedures.fast(0)
                p.checkpoint()
                p.procedures.slow(0)
                p.checkpoint()
