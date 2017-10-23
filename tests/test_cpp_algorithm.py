from tempfile import TemporaryDirectory
from unittest.case import TestCase

import turingarena.sandbox.compile


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
            turingarena.sandbox.compile.compile(source_filename, algorithm_name="test")
