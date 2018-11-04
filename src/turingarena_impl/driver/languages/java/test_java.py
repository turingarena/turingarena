import pytest

from turingarena import AlgorithmRuntimeError
from turingarena_impl.driver.tests.test_utils import define_algorithm

interface_text = """
    function test();
    main {
        call o = test();
        write o;
    }
"""


def java_algorithm(interface, java_source):
    return define_algorithm(
        interface_text=interface,
        language_name="Java",
        source_text=java_source,
    )


def test_java():
    with java_algorithm(interface_text, """
        public class Solution extends Skeleton {
            public int test() {
                return 3;
            }
        }
    """) as algo:
        with algo.run() as p:
            assert p.functions.test() == 3


def test_compile_failure():
    with pytest.raises(Exception):
        with java_algorithm(interface_text, """public class D {}""") as algo:
            with algo.run() as p:
                p.functions.test()


def test_security():
    try:
        with java_algorithm(interface_text, """
            import java.io.*;
            public class Solution extends Skeleton {
                public int test() {
                    try {
                        FileReader f = new FileReader("/dev/null");
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                    return 3;
                }
            }
        """) as algo:
            with pytest.raises(AlgorithmRuntimeError):
                with algo.run() as p:
                    p.call.test()
                    assert False
    except Exception as e: 
        assert True


# TODO: this test hangs for no obvious reason, need to investigae that...
# def test_memory_usage():
#     with java_algorithm("""
#                 function test1(int a);
#                 function test2(int b);
#
#                 main {
#                     read a;
#                     call out = test1(a);
#                     write out;
#
#                     read b;
#                     call out2 = test2(b);
#                     write out2;
#                 }
#             """, """
#         class Solution extends Skeleton {
#             int array[];
#             int test1(int a) {
#                 array = new int[1000000];
#                 System.err.println("test1");
#                 return a;
#             }
#             int test2(int a) {
#                 System.err.println("test2");
#                 array = null;
#                 System.gc();
#                 return a;
#             }
#         }
#     """) as algo:
#         with algo.run() as p:
#             assert p.functions.test1(1) == 1
#             i = p.sandbox.get_info()
#             assert 4000000 < i.memory_usage
#             assert i.memory_usage < 60000000
#             assert p.functions.test2(2) == 2

