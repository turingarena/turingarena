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

    def visit_Callback(self, n):
        self.line(f"{self.visit(n.prototype)} {{")
        with self.indent():
            self.visit(n.body)
        self.line("}")

    def visit_Call(self, n):
        method = n.method

        if method.callbacks:
            self.line("{")
            self.indentation += 1
            for c in n.callbacks:
                self.visit(c)

        value_arguments = [self.visit(p) for p in n.arguments]
        callback_arguments = [c.prototype.name for c in n.callbacks]

        parameters = ", ".join(value_arguments + callback_arguments)
        if method.has_return_value:
            return_value = f"{self.visit(n.return_value)} = "
        else:
            return_value = ""

        self.line(f"{return_value}{method.name}({parameters});")
        if method.callbacks:
            self.indentation -= 1
            self.line("}")
