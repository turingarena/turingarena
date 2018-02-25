from contextlib import contextmanager

import pytest

from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.test_utils import define_many

protocol_text = """
    function test() -> int;
    main {
        var int o;
        call test() -> o;
        output o;
    }
"""


@contextmanager
def cpp_algorithm(source):
    return define_many(
        interface_text=protocol_text,
        sources={"c++": source},
    )


def should_raise(cpp_source):
    with cpp_algorithm(cpp_source) as algo:
        with pytest.raises(AlgorithmRuntimeError) as excinfo:
            with algo.run() as (process, proxy):
                proxy.test()
    assert "Bad system call" in excinfo.value.stacktrace
    return excinfo


def should_succeed(cpp_source):
    with cpp_algorithm(cpp_source) as algo:
        with algo.run() as (process, proxy):
            proxy.test()


def test_open():
    excinfo = should_raise(r"""
        #include <cstdio>
        int test() { fopen("name", "r"); }
    """)
    assert "test ()" in excinfo.value.stacktrace


def test_constructor():
    excinfo = should_raise(r"""
        #include <stdio.h>
        __attribute__((constructor(0))) static void init() { fopen("name", "r"); }
        int test() {}
    """)
    assert "init ()" in excinfo.value.stacktrace


def test_istream():
    excinfo = should_raise(r"""
        #include <fstream>
        int test() { std::ifstream in("name"); }
    """)
    assert "test ()" in excinfo.value.stacktrace


def test_malloc_succeeds():
    should_succeed(r"""
        #include <cstdlib>
        #include <cstring>
        int test() {
            /* 10b (should use brk) */
            void *small = malloc(10);
            memset(small, 42, 10);

            /* 1Gb (should use mmap) */
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
        
            /* 1Gb (should use mmap) */
            std::vector<char> v2(1000 * 1000);
            for (int i = 0; i < v2.size(); i++) v2[i] = '0';
        }
    """)
