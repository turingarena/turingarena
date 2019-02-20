from turingarena.driver.languages.cpp import CppCodeGen


class CCodeGen(CppCodeGen):
    def visit_Interface(self, n):
        self.line("#include <stdio.h>")
        self.line("#include <stdlib.h>")
        self.line()
        for c in n.constants:
            self.visit(c)
            self.line()
        self.line()
        for m in n.methods:
            self.line(f"{self.visit(m)};")
            self.line()
        self.line()
        self.line("int main() {")
        with self.indent():
            self.visit(n.main)
        self.line("}")

    def visit_Alloc(self, n):
        reference = self.visit(n.reference)
        size = self.visit(n.size)
        self.line(f"{reference} = malloc({size} * sizeof(*{reference}));")
