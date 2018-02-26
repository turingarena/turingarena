from turingarena.test_utils import define_interface, define_algorithm


def test_get_time_usage():
    with define_interface("""
        function test(int i) -> int;
        main {
            var int i1, i2, o1, o2;
            input i1;
            call test(i1) -> o1;
            output o1;
            flush;
            input i2;
            call test(i2) -> o2;
            output o2;
        }
    """) as iface:
        with define_algorithm(
                interface=iface,
                language="c++",
                source_text="""
                    int test(int i) {
                        char x[2 * 1024 * 1024];
                        for(int j = 0; j < 100 * 1000 * 1000; j++) {
                            i = x[j%1024] = j^i^x[j%1024];
                        }
                        return i;
                    }
                """
        ) as algo:
            with algo.run() as (process, proxy):
                proxy.test(0)
                info = process.get_info()
                proxy.test(1)
    assert 0 < info.time_usage < 0.5
    assert 2 * 1024 * 1024 < info.memory_usage < 3 * 1024 * 1024
