from turingarena.driver.generator import InterfaceCodeGen, SkeletonCodeGen, TemplateCodeGen


class CppCodeGen(InterfaceCodeGen):
    def visit_ParameterDeclaration(self, d):
        indirections = "*" * d.dimensions
        return f"int {indirections}{d.variable.name}"

    def build_signature(self, callable, callbacks):
        return_type = "int" if callable.has_return_value else "void"
        value_parameters = [self.visit(p) for p in callable.parameter_declarations]
        callback_parameters = [
            self.build_signature(callback, [])
            for callback in callbacks
        ]
        parameters = ", ".join(value_parameters + callback_parameters)
        return f"{return_type} {callable.name}({parameters})"

    def build_method_signature(self, func):
        return self.build_signature(func, func.callbacks)

    def line_comment(self, comment):
        return f"// {comment}"


class CppSkeletonCodeGen(CppCodeGen, SkeletonCodeGen):
    def generate_header(self, interface):
        yield "#include <cstdio>"
        yield "#include <cstdlib>"
        yield "#include <cassert>"
        yield

    def visit_VariableDeclaration(self, d):
        pointers = "*" * d.dimensions
        yield f"static int {pointers}{d.variable.name};"

    def visit_ReferenceAllocation(self, a):
        name = a.reference.variable.name
        indexes = "".join(f"[{idx.name}]" for idx in a.reference.indexes)
        dimensions = "*" * a.dimensions
        size = self.visit(a.size)
        yield f"{name}{indexes} = new int{dimensions}[{size}];"

    def visit_MethodPrototype(self, m):
        yield f"{self.build_method_signature(m)};"

    def generate_main_block(self, interface):
        yield
        yield "int main() {"
        with self.indent():
            yield from self.visit(interface.main_block)
        yield "}"

    def visit_CallbackImplementation(self, callback):
        params = ", ".join(f"int {parameter.name}" for parameter in callback.prototype.parameters)
        if callback.prototype.has_return_value:
            return_value = " -> int"
        else:
            return_value = ""

        yield f"auto _callback_{callback.prototype.name} = []({params}){return_value}" " {"
        with self.indent():
            yield from self.visit(callback.body)
        yield "};"

    def visit_ConstantDeclaration(self, m):
        yield f"static const int {m.variable.name} = {self.visit(m.value)};"

    def call_statement_body(self, call_statement):
        method = call_statement.method

        for callback in call_statement.callbacks:
            yield from self.visit_CallbackImplementation(callback)

        value_arguments = [self.visit(p) for p in call_statement.arguments]
        callback_arguments = [
            f"_callback_{callback_signature.name}"
            for callback_signature in method.callbacks
        ]
        parameters = ", ".join(value_arguments + callback_arguments)
        if method.has_return_value:
            return_value = f"{self.visit(call_statement.return_value)} = "
        else:
            return_value = ""

        yield f"{return_value}{method.name}({parameters});"

    def visit_Call(self, call_statement):
        if call_statement.method.has_callbacks:
            yield "{"
            with self.indent():
                yield from self.call_statement_body(call_statement)
            yield "}"
        else:
            yield from self.call_statement_body(call_statement)

    def visit_Print(self, write_statement):
        format_string = " ".join("%d" for _ in write_statement.arguments) + r"\n"
        args = ", ".join(self.visit(v) for v in write_statement.arguments)
        yield f"""printf("{format_string}", {args});"""

    def visit_Read(self, statement):
        format_string = "".join("%d" for _ in statement.arguments)
        scanf_args = ", ".join("&" + self.visit(v) for v in statement.arguments)
        yield f"""scanf("{format_string}", {scanf_args});"""

    def visit_If(self, statement):
        condition = self.visit(statement.condition)
        yield f"if ({condition})" " {"
        with self.indent():
            yield from self.visit(statement.then_body)
        if statement.else_body:
            yield "} else {"
            with self.indent():
                yield from self.visit(statement.else_body)
        yield "}"

    def visit_For(self, s):
        index_name = s.index.variable.name
        size = self.visit(s.index.range)
        yield f"for (int {index_name} = 0; {index_name} < {size}; {index_name}++)" " {"
        with self.indent():
            yield from self.visit(s.body)
        yield "}"

    def visit_Loop(self, statement):
        yield "while (true) {"
        with self.indent():
            yield from self.visit(statement.body)
        yield "}"

    def visit_Switch(self, statement):
        for i, case in enumerate(statement.cases):
            condition = " || ".join(
                f"{self.visit(statement.value)} == {self.visit(label)}"
                for label in case.labels
            )
            if i == 0:
                yield f"if ({condition}) {{"
            else:
                yield f"}} else if ({condition}) {{"
            with self.indent():
                yield from self.visit(case.body)
        yield "}"

    def visit_Exit(self, statement):
        yield "exit(0);"

    def visit_Return(self, statement):
        yield f"return {self.visit(statement.value)};"

    def visit_Break(self, statement):
        yield "break;"

    def generate_flush(self):
        yield "fflush(stdout);"


class CppTemplateCodeGen(CppCodeGen, TemplateCodeGen):
    def visit_ConstantDeclaration(self, m):
        yield f"const int {m.variable.name} = {self.visit(m.value)};"

    def visit_MethodPrototype(self, m):
        yield
        if m.description is not None:
            for line in m.description.split("\n"):
                yield self.line_comment(line)
        yield f"{self.build_method_signature(m)}" " {"
        with self.indent():
            yield "// TODO"
            if m.has_return_value:
                yield "return 42;"
        yield "}"
