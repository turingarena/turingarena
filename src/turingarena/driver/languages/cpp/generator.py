from turingarena.driver.generator import InterfaceCodeGen, SkeletonCodeGen, TemplateCodeGen


class CppCodeGen(InterfaceCodeGen):
    def visit_Parameter(self, d):
        indirections = "*" * d.dimensions
        return f"int {indirections}{d.variable.name}"

    def build_signature(self, callable, callbacks):
        return_type = "int" if callable.has_return_value else "void"
        value_parameters = [self.visit(p) for p in callable.parameters]
        callback_parameters = [
            self.build_signature(callback, [])
            for callback in callbacks
        ]
        parameters = ", ".join(value_parameters + callback_parameters)
        return f"{return_type} {callable.name}({parameters})"

    def build_method_signature(self, func):
        return self.build_signature(func, func.callbacks)

    def line_comment(self, comment):
        self.line(f"// {comment}")


class CppSkeletonCodeGen(CppCodeGen, SkeletonCodeGen):
    def generate_header(self, interface):
        self.line("#include <cstdio>")
        self.line("#include <cstdlib>")
        self.line("#include <cassert>")
        self.line()

    def visit_VariableDeclaration(self, d):
        pointers = "*" * d.dimensions
        self.line(f"static int {pointers}{d.variable.name};")

    def visit_ReferenceAllocation(self, a):
        reference = self.visit(a.reference)
        dimensions = "*" * a.dimensions
        size = self.visit(a.size)
        self.line(f"{reference} = new int{dimensions}[{size}];")

    def visit_MethodPrototype(self, m):
        self.line(f"{self.build_method_signature(m)};")

    def generate_main_block(self, interface):
        self.line()
        self.line("int main() {")
        with self.indent():
            self.visit(interface.main_block)
        self.line("}")

    def visit_Callback(self, callback):
        params = ", ".join(self.visit(p) for p in callback.prototype.parameters)
        if callback.prototype.has_return_value:
            return_value = " -> int"
        else:
            return_value = ""

        with self.collect_lines() as c:
            self.line(f"[]({params}){return_value}" " {")
            with self.indent():
                self.visit(callback.body)
            self.line("}")
        return c.as_inline()

    def visit_Constant(self, m):
        self.line(f"static const int {m.variable.name} = {self.visit(m.value)};")

    def visit_Call(self, call_statement):
        method = call_statement.method

        value_arguments = [self.visit(p) for p in call_statement.arguments]
        callback_arguments = [self.visit(c) for c in call_statement.callbacks]

        parameters = ", ".join(value_arguments + callback_arguments)
        if method.has_return_value:
            return_value = f"{self.visit(call_statement.return_value)} = "
        else:
            return_value = ""

        self.line(f"{return_value}{method.name}({parameters});")

    def visit_Print(self, write_statement):
        format_string = " ".join("%d" for _ in write_statement.arguments) + r"\n"
        args = ", ".join(self.visit(v) for v in write_statement.arguments)
        self.line(f"""printf("{format_string}", {args});""")

    def visit_Read(self, statement):
        format_string = "".join("%d" for _ in statement.arguments)
        scanf_args = ", ".join("&" + self.visit(v) for v in statement.arguments)
        self.line(f"""scanf("{format_string}", {scanf_args});""")

    def visit_If(self, statement):
        condition = self.visit(statement.condition)
        self.line(f"if ({condition})" " {")
        with self.indent():
            self.visit(statement.then_body)
        if statement.else_body:
            self.line("} else {")
            with self.indent():
                self.visit(statement.else_body)
        self.line("}")

    def visit_For(self, s):
        index_name = s.index.variable.name
        size = self.visit(s.index.range)
        self.line(f"for (int {index_name} = 0; {index_name} < {size}; {index_name}++)" " {")
        with self.indent():
            self.visit(s.body)
        self.line("}")

    def visit_Loop(self, statement):
        self.line("while (true) {")
        with self.indent():
            self.visit(statement.body)
        self.line("}")

    def visit_Switch(self, statement):
        for i, case in enumerate(statement.cases):
            condition = " || ".join(
                f"{self.visit(statement.value)} == {self.visit(label)}"
                for label in case.labels
            )
            if i == 0:
                self.line(f"if ({condition}) {{")
            else:
                self.line(f"}} else if ({condition}) {{")
            with self.indent():
                self.visit(case.body)
        self.line("}")

    def visit_Exit(self, statement):
        self.line("exit(0);")

    def visit_Return(self, statement):
        self.line(f"return {self.visit(statement.value)};")

    def visit_Break(self, statement):
        self.line("break;")

    def generate_flush(self):
        self.line("fflush(stdout);")


class CppTemplateCodeGen(CppCodeGen, TemplateCodeGen):
    def visit_Constant(self, m):
        self.line(f"const int {m.variable.name} = {self.visit(m.value)};")

    def visit_MethodPrototype(self, m):
        self.line()
        if m.description is not None:
            for line in m.description.split("\n"):
                self.line_comment(line)
        self.line(f"{self.build_method_signature(m)}" " {")
        with self.indent():
            self.line("// TODO")
            if m.has_return_value:
                self.line("return 42;")
        self.line("}")
