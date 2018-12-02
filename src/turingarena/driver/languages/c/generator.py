from turingarena.driver.languages.cpp import CppCodeGen


class CCodeGen(CppCodeGen):
    def visit_Interface(self, n):
        self.line("#include <cstdio>")
        self.line("#include <cstdlib>")
        self.line("#include <cassert>")
        self.line()
        for c in n.constants:
            self.visit(c)
            self.line()
        self.line('extern "C" {')
        self.line()
        for m in n.methods:
            self.line(f"{self.visit(m)};")
            self.line()
        self.line('} // extern "C"')
        self.line()
        self.line("int main() {")
        with self.indent():
            self.visit(n.main)
        self.line("}")
