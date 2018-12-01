from turingarena.driver.generator import InterfaceCodeGen, SkeletonCodeGen, TemplateCodeGen


class JavaCodeGen(InterfaceCodeGen):

    def visit_ParameterDeclaration(self, d):
        arrays = "[]" * d.dimensions
        return f"int {d.variable.name}{arrays}"

    def build_callbacks_interface_name(self, method):
        return f'{method.name}_callbacks'

    def build_signature(self, callable, callbacks):
        return_type = "int" if callable.has_return_value else "void"
        value_parameters = [self.visit(p) for p in callable.parameter_declarations]
        if callbacks:
            value_parameters.append(
                self.build_callbacks_interface_name(callable) + " callbacks")
        parameters = ", ".join(value_parameters)
        return f"{return_type} {callable.name}({parameters})"

    def build_method_signature(self, func):
        return self.build_signature(func, func.callbacks)

    def build_callback_signature(self, callback):
        return_type = "int" if callback.has_return_value else "void"
        value_parameters = [self.visit(p) for p in callback.parameter_declarations]
        parameters = ", ".join(value_parameters)
        return f"{return_type} {callback.name}({parameters})"

    def generate_footer(self, interface):
        return "}"

    def line_comment(self, comment):
        self.line(f"// {comment}")

    def generate_callbacks_declaration(self, callback):
        return f'{self.build_method_signature(callback)};'

    def visit_ConstantDeclaration(self, m):
        self.line(f"private static final {m.variable.name} = {self.visit(m.value)};")


class JavaSkeletonCodeGen(JavaCodeGen, SkeletonCodeGen):
    def generate_header(self, interface):
        self.line('import java.util.Scanner;')
        self.line()
        self.line('abstract class Skeleton {')
        with self.indent():
            self.line('private static final Scanner in = new Scanner(System.in);')

    def visit_VariableDeclaration(self, d):
        self.line(f'int{"[]" * d.dimensions} {d.variable.name};')

    def visit_ReferenceAllocation(self, a):
        reference = self.visit(a.reference)
        dimensions = "[]" * a.dimensions
        size = self.visit(a.size)
        self.line(f"{reference} = new int[{size}]{dimensions};")

    def visit_MethodPrototype(self, m):
        with self.indent():
            if m.callbacks:
                self.line(f'interface {self.build_callbacks_interface_name(m)} ''{')
                for cbks in m.callbacks:
                    self.line(self.generate_callbacks_declaration(cbks))
                self.line('}')

        self.line(f'abstract {self.build_method_signature(m)};')

    def generate_main(self, interface):
        self.line()
        self.line('public static void main(String args[]) {')
        with self.indent():
            self.line('Solution __solution = new Solution();')
            self.visit(interface.main_block)
        self.line('}')

    def generate_main_block(self, interface):
        with self.indent():
            self.generate_main(interface)

    def visit_CallbackImplementation(self, callback):
        self.line(f'public {self.build_callback_signature(callback.prototype)}' " {")
        with self.indent():
            self.visit(callback.body)
        self.line("}")

    def call_statement_body(self, call_statement):

        method = call_statement.method

        # build anonimous inner class
        if call_statement.callbacks:
            cb_name = self.build_callbacks_interface_name(method)
            self.line(cb_name + " __clbks = new " + cb_name + "() {")
            with self.indent():
                for callback in call_statement.callbacks:
                    self.visit_CallbackImplementation(callback)
            self.line("};")

        value_arguments = [self.visit(p) for p in call_statement.arguments]
        if method.callbacks:
            value_arguments.append("__clbks")

        parameters = ", ".join(value_arguments)

        if method.has_return_value:
            return_value = f"{self.visit(call_statement.return_value)} = "
        else:
            return_value = ""

        self.line(f"{return_value}__solution.{method.name}({parameters});")

    def visit_Call(self, call_statement):
        self.call_statement_body(call_statement)

    def visit_Print(self, statement):
        format_string = ' '.join('%d' for _ in statement.arguments) + r'\n'
        args = ', '.join(self.visit(v) for v in statement.arguments)
        self.line(f'System.out.printf("{format_string}", {args});')

    def visit_Read(self, statement):
        for arg in statement.arguments:
            self.line(f'{self.visit(arg)} = in.nextInt();')

    def visit_If(self, statement):
        condition = self.visit(statement.condition)
        self.line(f'if ({condition})'' {')
        with self.indent():
            self.visit(statement.then_body)
        if statement.else_body is not None:
            self.line('} else {')
            with self.indent():
                self.visit(statement.else_body)
        self.line('}')

    def visit_For(self, statement):
        index_name = statement.index.variable.name
        size = self.visit(statement.index.range)
        self.line(f'for (int {index_name} = 0; {index_name} < {size}; {index_name}++)'' {')
        with self.indent():
            self.visit(statement.body)
        self.line('}')

    def visit_Loop(self, loop_statement):
        self.line('while (true) {')
        with self.indent():
            self.visit(loop_statement.body)
        self.line('}')

    def build_switch_cases(self, variable, labels):
        variable = self.visit(variable)
        return ' || '.join(f'{variable} == {label}' for label in labels)

    def visit_Switch(self, switch_statement):
        cases = [case for case in switch_statement.cases]
        self.line(f'if ({self.build_switch_condition(switch_statement.value, cases[0].labels)})'' {')
        with self.indent():
            self.visit(cases[0].body)
        for case in cases[1:]:
            self.line('}' f' else if ({self.build_switch_condition(switch_statement.value, case.labels)}) ' '{')
            with self.indent():
                self.visit(case.body)
        self.line('}')

    def generate_flush(self):
        self.line('System.out.flush();')

    def visit_Exit(self, exit_statement):
        self.line('System.exit(0);')

    def visit_Return(self, return_statement):
        self.line(f'return {self.visit(return_statement.value)};')

    def visit_Break(self, break_statement):
        self.line('break;')


class JavaTemplateCodeGen(JavaCodeGen, TemplateCodeGen):
    def generate_header(self, interface):
        self.line('class Solution extends Skeleton {')

    def visit_MethodPrototype(self, m):
        with self.indent():
            if m.callbacks:
                self.line()
                self.line_comment(f'interface {self.build_callbacks_interface_name(m)} ''{')
                for cbks in m.callbacks:
                    self.line_comment(self.generate_callbacks_declaration(cbks))
                self.line_comment('}')

            self.line()
            self.line(f"{self.build_method_signature(m)}" " {")
            with self.indent():
                self.line('// TODO')
                if m.has_return_value:
                    self.line("return 42;")
            self.line('}')
