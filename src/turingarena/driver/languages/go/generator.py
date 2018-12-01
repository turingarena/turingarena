from turingarena.driver.generator import InterfaceCodeGen, SkeletonCodeGen, TemplateCodeGen


class GoCodeGen(InterfaceCodeGen):
    def visit_Parameter(self, d):
        indirections = "[]" * d.dimensions
        return f"{d.variable.name} {indirections}int"

    def build_signature(self, callable, callbacks, param=False):
        return_type = " int" if callable.has_return_value else ""
        value_parameters = [self.visit(p) for p in callable.parameters]
        callback_parameters = [
            self.build_signature(callback, [], param=True)
            for callback in callbacks
        ]
        parameters = ", ".join(value_parameters + callback_parameters)
        if param:
            return f"{callable.name} func({parameters}){return_type}"
        else:
            return f"func {callable.name}({parameters}){return_type}"

    def build_method_signature(self, func):
        return self.build_signature(func, func.callbacks)

    def line_comment(self, comment):
        self.line(f"// {comment}")


class GoSkeletonCodeGen(GoCodeGen, SkeletonCodeGen):
    def generate_header(self, interface):
        self.line("package main")
        self.line()
        self.line('import "fmt"')
        self.line('import "os"')
        self.line()

    def visit_VariableDeclaration(self, d):
        self.line(f"var {d.variable.name} {'[]' * d.dimensions + 'int'}")

    def visit_MethodPrototype(self, m):
        return []

    def visit_Constant(self, m):
        return []

    def visit_ReferenceAllocation(self, a):
        reference = self.visit(a.reference)
        # FIXME: is this + 1 needed?
        dimensions = "[]" * (a.dimensions + 1)
        size = self.visit(a.size)
        self.line(f"{reference} = make({dimensions}int, {size})")

    def generate_main_block(self, interface):
        self.line("func main() {")
        with self.indent():
            self.visit(interface.main_block)
        self.line("}")

    def visit_Callback(self, callback):
        params = ", ".join(self.visit(p) for p in callback.prototype.parameters) + " int"
        if callback.prototype.has_return_value:
            return_value = "int"
        else:
            return_value = ""

        self.line(f"_callback_{callback.prototype.name} := func({params}) {return_value}" " {")
        with self.indent():
            self.visit(callback.body)
        self.line("}")

    def call_statement_body(self, call_statement):
        method = call_statement.method

        for callback in call_statement.callbacks:
            self.visit_Callback(callback)

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

        self.line(f"{return_value}{method.name}({parameters});")

    def visit_Call(self, call_statement):
        if call_statement.method.callbacks:
            self.line("{")
            with self.indent():
                self.call_statement_body(call_statement)
            self.line("}")
        else:
            self.call_statement_body(call_statement)

    def visit_Print(self, write_statement):
        format_string = " ".join("%d" for _ in write_statement.arguments) + r"\n"
        args = ", ".join(self.visit(v) for v in write_statement.arguments)
        self.line(f'fmt.Printf("{format_string}", {args})')

    def visit_Read(self, statement):
        format_string = "".join("%d" for _ in statement.arguments)
        scanf_args = ", ".join("&" + self.visit(v) for v in statement.arguments)
        self.line(f'fmt.Scanf("{format_string}", {scanf_args});')

    def visit_If(self, statement):
        condition = self.visit(statement.condition)
        self.line(f"if {condition}" " {")
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
        self.line(f"for {index_name} := 0; {index_name} < {size}; {index_name}++" " {")
        with self.indent():
            self.visit(s.body)
        self.line("}")

    def visit_Loop(self, statement):
        self.line("for {")
        with self.indent():
            self.visit(statement.body)
        self.line("}")

    def build_switch_condition(self, variable, labels):
        variable = self.visit(variable)
        return " || ".join(f"{variable} == {label}" for label in labels)

    def visit_Switch(self, statement):
        self.line("switch {")
        for case in statement.cases:
            self.line(f"case {self.build_switch_condition(statement.variable, case.labels)}:")
            with self.indent():
                self.visit(case.body)
        self.line("}")

    def visit_Exit(self, statement):
        self.line("os.Exit(0)")

    def visit_Return(self, statement):
        self.line(f"return {self.visit(statement.value)};")

    def visit_Break(self, statement):
        self.line("break")

    def generate_flush(self):
        self.line("os.Stdout.Sync()")


class GoTemplateCodeGen(GoCodeGen, TemplateCodeGen):
    def visit_Constant(self, m):
        self.line(f"const {m.variable.name} = {self.visit(m.value)}")

    def visit_MethodPrototype(self, m):
        self.line()
        self.line(f"{self.build_method_signature(m)}" " {")
        with self.indent():
            self.line("// TODO")
        self.line("}")
