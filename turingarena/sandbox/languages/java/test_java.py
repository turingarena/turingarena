import pytest

from turingarena.sandbox.exceptions import AlgorithmRuntimeError, CompilationFailed
from turingarena.algorithm import load_algorithm

interface_text = """
    function test() -> int;
    main {
        var int o;
        call test() -> o;
        output o;
    }
"""


def java_algorithm(interface, java_source):
    return load_algorithm(
        interface_text=interface,
        language="java",
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
            assert p.call.test() == 3


def test_security():
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


def test_compile_failure():
    with pytest.raises(CompilationFailed) as e:
        with java_algorithm(interface_text, """public class D {}""") as algo:
            with algo.run() as p:
                p.call.test()
    print(e.value.compilation_output)


def test_memory_usage():
    with java_algorithm("""
                function test1(int a) -> int;
                function test2(int b) -> int;
                
                main {
                    var int a, out; 
                    input a; 
                    call test1(a) -> out;
                    output out; 
                    flush;
                    var int b, out2; 
                    input b; 
                    call test2(b) -> out2;
                    output out2;
                    flush;
                }
            """, """
        class Solution extends Skeleton {
            int array[];
            int test1(int a) {
                array = new int[1000000];
                System.err.println("test1");
                return a;
            }
            int test2(int a) {
                System.err.println("test2");
                array = null;
                System.gc(); 
                return a;
            }
        }
    """) as algo:
        with algo.run() as p:
            assert p.call.test1(1) == 1
            i = p.sandbox.get_info()
            assert 4000000 < i.memory_usage < 6000000
            assert p.call.test2(2) == 2
