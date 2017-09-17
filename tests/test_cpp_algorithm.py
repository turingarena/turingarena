import io

import sys
from unittest.case import TestCase

from turingarena.runner.cpp import run_cpp


class Test(TestCase):
    def test(self):
        process = run_cpp(
            io.StringIO("""
                int a;
            """),
            io.StringIO(r"""
                #include <cstdio>            

                int main() {
                    printf("3\n");
                    return 0;
                }
            """)
        )

        output, error = process.communicate()
        print(output)

    def test_compilation_failed(self):
        process = run_cpp(
            io.StringIO("""
                int a;
            """),
            io.StringIO(r"""
                #include <cstdio>            

                int main() {
                    c = 3; // undefined
                    printf("3\n");
                    return 0;
                }
            """)
        )

        output, error = process.communicate()
        print(output)
