from pytest import raises
from turingarena import TimeLimitExceeded
from turingarena_impl.driver.tests.test_utils import define_algorithm


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


def test_time_usage_section():
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


def test_time_limit_section():
    with my_algo() as algo:
        with algo.run() as p:
            with p.section(time_limit=0.001):
                p.procedures.fast(0)
                p.checkpoint()
            with raises(TimeLimitExceeded):
                with p.section(time_limit=0.001):
                    p.procedures.slow(0)
                    p.checkpoint()
