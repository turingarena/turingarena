from pytest import approx

from turingarena.interface.algorithm import load_algorithm


def test_get_time_memory_usage():
    with load_algorithm(
            interface_text="""
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
            """,
            language="c++",
            source_text="""
                int test(int i) {
                    char x[1024 * 1024];
                    for(int j = 0; j < 100 * 1000 * 1000; j++) {
                        i = x[j%1024] = j^i^x[j%1024];
                    }
                    return i;
                }
            """
    ) as algo:
        with algo.run() as p:
            with p.section() as section1:
                p.call.test(1)
            info1 = p.sandbox.get_info()
            with p.section() as section2:
                p.call.test(2)
            info2 = p.sandbox.get_info()

    assert 0 < section1.time_usage == info1.time_usage < 0.5
    assert 0 < section2.time_usage < 0.5

    assert section1.time_usage + section2.time_usage == approx(info2.time_usage)

    assert 1024 * 1024 < info1.memory_usage < 2 * 1024 * 1024
    assert info2.memory_usage == 0
