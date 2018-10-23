from turingarena_impl.driver.tests.test_utils import define_algorithms


def test_time_limit_section():
    for algo in define_algorithms(
            interface_text="""
                procedure p(a);
                main {
                    checkpoint;
                    read a;
                    call p(a);
                    checkpoint;
                }
            """,
            sources={
                'C++': """
                    void p(int a) {
                        for(int i = 0; i < 1000000; i++);
                    }
                """,
            },
    ):
        with algo.run() as p:
            p.checkpoint()
            with p.section() as s:
                p.procedures.p(0)
                p.checkpoint()
        assert 0.00001 < s.time_usage < 0.01
