import pytest

from turingarena.algorithm import Algorithm
from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.sandbox.languages import cpp

protocol_text = """
    function test() -> int;
    main {
        var int o;
        call test() -> o;
        write o;
    }
"""


def cpp_algorithm(source):
    return Algorithm.load(
        interface_text=protocol_text,
        language=cpp.language,
        source_text=source,
    )


def should_raise(cpp_source):
    with cpp_algorithm(cpp_source) as algo:
        with pytest.raises(AlgorithmRuntimeError) as excinfo:
            with algo.run() as p:
                p.call.test()
    return excinfo


def should_succeed(cpp_source):
    with cpp_algorithm(cpp_source) as algo:
        with algo.run() as p:
            p.call.test()


def expect_bad_syscall(code, where):
    excinfo = should_raise(code)
    assert "Bad system call" in excinfo.value.stacktrace
    assert where in excinfo.value.stacktrace


def test_open():
    expect_bad_syscall(r"""
        #include <cstdio>
        int test() { fopen("name", "r"); }
    """, "test ()")


def test_constructor():
    expect_bad_syscall(r"""
        #include <stdio.h>
        __attribute__((constructor(0))) static void init() { fopen("name", "r"); }
        int test() {}
    """, "init ()")


def test_istream():
    expect_bad_syscall(r"""
        #include <fstream>
        int test() { std::ifstream in("name"); }
    """, "test ()")


def test_malloc_succeeds():
    should_succeed(r"""
        #include <cstdlib>
        #include <cstring>
        int test() {
            /* 10b (should use brk) */
            void *small = malloc(10);
            memset(small, 42, 10);

            /* 1Mb (should use mmap) */
            void *big = malloc(1000 * 1000);
            memset(big, 42, 1000 * 1000);

            free(small);
            free(big);
        }
    """)


def test_vector_succeeds():
    should_succeed(r"""
        #include <vector>
        int test() {
            /* 10b (should use brk) */
            std::vector<char> v(10);
            for (int i = 0; i < v.size(); i++) v[i] = '0';
        
            /* 1Mb (should use mmap) */
            std::vector<char> v2(1000 * 1000);
            for (int i = 0; i < v2.size(); i++) v2[i] = '0';
        }
    """)


def test_time_limit():
    excinfo = should_raise("""
        int test() { for(;;) {} }
    """)
    assert "CPU time limit exceeded" in excinfo.value.stacktrace


def test_memory_limit_static():
    should_raise("""
        const int size = 1 * 1024 * 1024 * 1024;
        char big[size];
        int test() {}
    """)


def test_memory_limit_malloc():
    should_succeed(r"""
        #include <cstdlib>
        #include <cstring>
        #include <cassert>
        int test() {
            int size = 1 * 1024 * 1024 * 1024;
            char* a = (char*) malloc(size);
            assert(a == NULL);
        }
    """)


def test_memory_limit_new():
    should_raise("""
        int test() { new int[1 * 1024 * 1024 * 1024]; }
    """)


def test_segmentation_fault():
    excinfo = should_raise("""
        int test() { *((int*) 0) = 1; }
    """)
    assert "Segmentation fault" in excinfo.value.stacktrace


def test_get_time_memory_usage():
    with Algorithm.load(
            interface_text="""
                function test(int i) -> int;
                main {
                    var int i1, i2, o1, o2;
                    read i1;
                    call test(i1) -> o1;
                    write o1;
                    flush;
                    read i2;
                    call test(i2) -> o2;
                    write o2;
                }
            """,
            language=cpp.language,
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

    assert section1.time_usage + section2.time_usage == pytest.approx(info2.time_usage)

    assert 1024 * 1024 < info1.memory_usage < 2 * 1024 * 1024
    assert info2.memory_usage == 0
