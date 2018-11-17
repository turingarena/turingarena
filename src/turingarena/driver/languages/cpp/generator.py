from turingarena.driver.generator import InterfaceCodeGen, SkeletonCodeGen, TemplateCodeGen


class CppCodeGen(InterfaceCodeGen):
    def build_parameter(self, parameter):
        indirections = "*" * parameter.dimensions
        return f"int {indirections}{parameter.name}"

    def build_signature(self, callable, callbacks):
        return_type = "int" if callable.has_return_value else "void"
        value_parameters = [self.build_parameter(p) for p in callable.parameters]
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
        pointers = "*" * d.variable.dimensions
        yield f"static int {pointers}{d.variable.name};"

    def visit_VariableAllocation(self, a):
        name = a.variable.name
        indexes = "".join(f"[{idx.variable.name}]" for idx in a.indexes)
        dimensions = "*" * (a.variable.dimensions - len(indexes) - 1)
        size = self.visit(a.size)
        yield f"{name}{indexes} = new int{dimensions}[{size}];"

    def visit_MethodPrototype(self, m):
        yield f"{self.build_method_signature(m)};"

    def generate_main_block(self, interface):
        yield
        yield "int main() {"
        yield from self.block(interface.main_block)
        yield "}"

    def generate_callback(self, callback):
        params = ", ".join(f"int {parameter.name}" for parameter in callback.parameters)
        if callback.has_return_value:
            return_value = " -> int"
        else:
            return_value = ""

        yield f"auto _callback_{callback.name} = []({params}){return_value}" " {"
        yield from self.block(callback.body)
        yield "};"

    def generate_constant_declaration(self, name, value):
        yield f"static const int {name} = {value};"

    def call_statement_body(self, call_statement):
        method = call_statement.method

        for callback in call_statement.callbacks:
            yield from self.generate_callback(callback)

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

    def visit_CallStatement(self, call_statement):
        if call_statement.method.has_callbacks:
            yield "{"
            yield from self.indent_all(self.call_statement_body(call_statement))
            yield "}"
        else:
            yield from self.call_statement_body(call_statement)

    def visit_OutputStatement(self, write_statement):
        format_string = " ".join("%d" for _ in write_statement.arguments) + r"\n"
        args = ", ".join(self.visit(v) for v in write_statement.arguments)
        yield f"""printf("{format_string}", {args});"""

    def visit_ReadStatement(self, statement):
        format_string = "".join("%d" for _ in statement.arguments)
        scanf_args = ", ".join("&" + self.visit(v) for v in statement.arguments)
        yield f"""scanf("{format_string}", {scanf_args});"""

    def visit_IfStatement(self, statement):
        condition = self.visit(statement.condition)
        yield f"if ({condition})" " {"
        yield from self.block(statement.then_body)
        if statement.else_body:
            yield "} else {"
            yield from self.block(statement.else_body)
        yield "}"

    def visit_ForStatement(self, s):
        index_name = s.index.variable.name
        size = self.visit(s.index.range)
        yield f"for (int {index_name} = 0; {index_name} < {size}; {index_name}++)" " {"
        yield from self.block(s.body)
        yield "}"

    def visit_LoopStatement(self, statement):
        yield "while (true) {"
        yield from self.block(statement.body)
        yield "}"

    def build_switch_condition(self, variable, labels):
        variable = self.visit(variable)
        return " || ".join(f"{variable} == {label}" for label in labels)

    def visit_SwitchStatement(self, statement):
        cases = [case for case in statement.cases]
        yield f"if ({self.build_switch_condition(statement.variable, cases[0].labels)}) " "{"
        yield from self.block(cases[0].body)
        for case in cases[1:]:
            yield "}" f" else if ({self.build_switch_condition(statement.variable, case.labels)}) " "{"
            yield from self.block(case.body)
        yield "}"

    def visit_ExitStatement(self, statement):
        yield "exit(0);"

    def visit_ReturnStatement(self, statement):
        yield f"return {self.visit(statement.value)};"

    def visit_BreakStatement(self, statement):
        yield "break;"

    def generate_flush(self):
        yield "fflush(stdout);"


class CppTemplateCodeGen(CppCodeGen, TemplateCodeGen):
    def generate_constant_declaration(self, name, value):
        yield f"const int {name} = {value};"

    def visit_MethodPrototype(self, m):
        yield
        if m.description is not None:
            for line in m.description.split("\n"):
                yield self.line_comment(line)
        yield f"{self.build_method_signature(m)}" " {"
        yield self.indent("// TODO")
        if m.has_return_value:
            yield self.indent("return 42;")
        yield "}"
