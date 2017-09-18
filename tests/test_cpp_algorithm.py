import io

import sys
from tempfile import TemporaryFile, TemporaryDirectory
from unittest.case import TestCase

from turingarena.runner import compile
from turingarena.runner.cpp import run_cpp


class Test(TestCase):
    def test(self):
        with TemporaryDirectory() as d:
            source_filename = d + "/source.cpp"
            with open(source_filename, "w") as source:
                source.write(r"""
                    #include <cstdio>            
    
                    int main() {
                        printf("3\n");
                        return 0;
                    }
                """)
            compile.compile(source_filename, algorithm_name="test")
