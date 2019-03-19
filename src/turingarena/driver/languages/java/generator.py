from turingarena.driver.gen.generator import InterfaceCodeGen


class JavaCodeGen(InterfaceCodeGen):

    def visit_Interface(self, n):
        self.line("import java.util.Scanner;")
        self.line()
        self.line("abstract class Skeleton {")
        with self.indent():
            self.line("private static final Scanner in = new Scanner(System.in);")
            self.line()
            for c in n.constants:
                self.visit(c)
            self.line()
            for m in n.methods:
                self.visit(m)
                self.line()
            self.line("public static void main(String[] args) {")
            with self.indent():
                self.line("Solution __solution = new Solution();")
                self.line()
                self.visit(n.main)
            self.line("}")
        self.line("}")

    def visit_InterfaceTemplate(self, n):
        self.line("class Solution extends Skeleton {")
        self.line()
        with self.indent():
            for m in n.methods:
                if m.description:
                    for l in m.description:
                        self.line(f"// {l}")
                self.line(f"{ self._build_method_signature(m.prototype) } {{")
                with self.indent():
                    self.visit(m.body)
                self.line("}")
        self.line("}")

    def visit_Parameter(self, d):
        arrays = "[]" * d.dimensions
        return f"int {d.variable.name}{arrays}"

    def _build_callbacks_interface_name(self, method):
        return f"{method.name.capitalize()}Callbacks"

    def _build_method_signature(self, method):
        return_type = "int" if method.has_return_value else "void"
        value_parameters = [self.visit(p) for p in method.parameters]
        if method.callbacks:
            value_parameters.append(
                self._build_callbacks_interface_name(method) + " callbacks")
        parameters = ", ".join(value_parameters)
        return f"{return_type} {method.name}({parameters})"

    def _build_callback_signature(self, callback):
        return_type = "int" if callback.has_return_value else "void"
        value_parameters = [self.visit(p) for p in callback.parameters]
        parameters = ", ".join(value_parameters)
        return f"{return_type} {callback.name}({parameters})"

    def visit_Comment(self, n):
        self.line(f"// {n.text}")

    def generate_callbacks_declaration(self, callback):
        return f"{ self._build_method_signature(callback) };"

    def visit_Constant(self, m):
        self.line(f"private static final int {m.variable.name} = {self.visit(m.value)};")

    def visit_VariableDeclaration(self, d):
        self.line(f'int{"[]" * d.dimensions} {d.variable.name};')

    def visit_Alloc(self, a):
        reference = self.visit(a.reference)
        dimensions = "[]" * a.dimensions
        size = self.visit(a.size)
        self.line(f"{reference} = new int[{size}]{dimensions};")

    def visit_Prototype(self, m):
        if m.callbacks:
            self.line(f"interface { self._build_callbacks_interface_name(m) } ""{")
            with self.indent():
                for cbks in m.callbacks:
                    self.line(self.generate_callbacks_declaration(cbks))
            self.line("}")
        self.line(f"abstract { self._build_method_signature(m) };")

    def visit_Callback(self, callback):
        self.line(f"public {self._build_callback_signature(callback.prototype)}" " {")
        with self.indent():
            self.visit(callback.body)
        self.line("}")

    def visit_Call(self, call_statement):
        method = call_statement.method

        if call_statement.callbacks:
            cb_name = self._build_callbacks_interface_name(method)
            self.line(cb_name + f" {method.name}Callbacks = new " + cb_name + "() {")
            with self.indent():
                for callback in call_statement.callbacks:
                    self.visit_Callback(callback)
            self.line("};")

        value_arguments = [self.visit(p) for p in call_statement.arguments]
        if method.callbacks:
            value_arguments.append(f" {method.name}Callbacks")

        parameters = ", ".join(value_arguments)
        return_value = f"{self.visit(call_statement.return_value)} = " if method.has_return_value else ""

        self.line(f"{return_value}__solution.{method.name}({parameters});")

    def visit_Print(self, statement):
        format_string = " ".join("%d" for _ in statement.arguments) + r"\n"
        args = ", ".join(self.visit(v) for v in statement.arguments)
        self.line(f'System.out.printf("{format_string}", {args});')

    def visit_Read(self, statement):
        for arg in statement.arguments:
            self.line(f"{self.visit(arg)} = in.nextInt();")

    def visit_If(self, statement):
        condition = self.visit(statement.condition)
        self.line(f"if ({condition} != 0) {{")
        with self.indent():
            self.visit(statement.branches.then_body)
        if statement.branches.else_body is not None:
            self.line("} else {")
            with self.indent():
                self.visit(statement.branches.else_body)
        self.line("}")

    def visit_For(self, statement):
        index_name = statement.index.variable.name
        size = self.visit(statement.index.range)
        self.line(f"for (int {index_name} = 0; {index_name} < {size}; {index_name}++)"" {")
        with self.indent():
            self.visit(statement.body)
        self.line("}")

    def visit_Loop(self, loop_statement):
        self.line("while (true) {")
        with self.indent():
            self.visit(loop_statement.body)
        self.line("}")

    def build_switch_cases(self, variable, labels):
        variable = self.visit(variable)
        return " || ".join(f"{variable} == {label}" for label in labels)

    def visit_Switch(self, switch_statement):
        cases = [case for case in switch_statement.cases]
        self.line(f"if ({self.build_switch_cases(switch_statement.value, cases[0].labels)})"" {")
        with self.indent():
            self.visit(cases[0].body)
        for case in cases[1:]:
            self.line("}" f" else if ({self.build_switch_cases(switch_statement.value, case.labels)}) " "{")
            with self.indent():
                self.visit(case.body)
        self.line("}")

    def visit_Flush(self, n):
        self.line("System.out.flush();")

    def visit_Exit(self, exit_statement):
        self.line("System.exit(0);")

    def visit_Return(self, return_statement):
        self.line(f"return {self.visit(return_statement.value)};")

    def visit_Break(self, break_statement):
        self.line("break;")
