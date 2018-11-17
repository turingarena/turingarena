from turingarena.driver.generator import InterfaceCodeGen, SkeletonCodeGen, TemplateCodeGen


class JavaCodeGen(InterfaceCodeGen):

    def build_parameter(self, parameter):
        arrays = "[]" * parameter.dimensions
        return f"int {parameter.name}{arrays}"

    def build_callbacks_interface_name(self, method):
        return f'{method.name}_callbacks'

    def build_signature(self, callable, callbacks):
        return_type = "int" if callable.has_return_value else "void"
        value_parameters = [self.build_parameter(p) for p in callable.parameters]
        if callbacks:
            value_parameters.append(
                self.build_callbacks_interface_name(callable) + " callbacks")
        parameters = ", ".join(value_parameters)
        return f"{return_type} {callable.name}({parameters})"

    def build_method_signature(self, func):
        return self.build_signature(func, func.callbacks)

    def build_callback_signature(self, callback):
        return_type = "int" if callback.has_return_value else "void"
        value_parameters = [self.build_parameter(p) for p in callback.parameters]
        parameters = ", ".join(value_parameters)
        return f"{return_type} {callback.name}({parameters})"

    def generate_footer(self, interface):
        return "}"

    def line_comment(self, comment):
        return f"// {comment}"

    def generate_callbacks_declaration(self, callback):
        return self.indent(f'{self.build_method_signature(callback)};')

    def generate_constant_declaration(self, name, value):
        yield f"private static final {name} = {value};"


class JavaSkeletonCodeGen(JavaCodeGen, SkeletonCodeGen):
    def generate_header(self, interface):
        yield 'import java.util.Scanner;'
        yield
        yield 'abstract class Skeleton {'
        yield self.indent('private static final Scanner in = new Scanner(System.in);')

    def visit_VariableDeclaration(self, d):
        yield f'int{"[]" * d.variable.dimensions} {d.variable.name};'

    def visit_VariableAllocation(self, a):
        name = a.variable.name
        indexes = "".join(f"[{idx.variable.name}]" for idx in a.indexes)
        dimensions = "[]" * (a.variable.dimensions - len(indexes) - 1)
        size = self.visit(a.size)
        yield f"{name}{indexes} = new int[{size}]{dimensions};"

    def generate_method_declaration(self, method_declaration):

        if method_declaration.callbacks:
            yield self.indent(f'interface {self.build_callbacks_interface_name(method_declaration)} ''{')
            for cbks in method_declaration.callbacks:
                yield self.indent(self.generate_callbacks_declaration(cbks))
            yield self.indent('}')

        yield self.indent(f'abstract {self.build_method_signature(method_declaration)};')

    def generate_main(self, interface):
        yield
        yield 'public static void main(String args[]) {'
        yield self.indent('Solution __solution = new Solution();')
        yield from self.block(interface.main_block)
        yield '}'

    def generate_main_block(self, interface):
        yield from self.indent_all(self.generate_main(interface))

    def generate_callback(self, callback):
        yield f'public {self.build_callback_signature(callback)}' " {"
        yield from self.block(callback.body)
        yield "}"
        pass

    def call_statement_body(self, call_statement):

        method = call_statement.method

        # build anonimous inner class
        if call_statement.callbacks:
            cb_name = self.build_callbacks_interface_name(method)
            yield cb_name + " __clbks = new " + cb_name + "() {"
            for callback in call_statement.callbacks:
                yield from self.indent_all(self.generate_callback(callback))
            yield "};"

        value_arguments = [self.visit(p) for p in call_statement.arguments]
        if method.callbacks:
            value_arguments.append("__clbks")

        parameters = ", ".join(value_arguments)

        if method.has_return_value:
            return_value = f"{self.visit(call_statement.return_value)} = "
        else:
            return_value = ""

        yield f"{return_value}__solution.{method.name}({parameters});"

    def visit_CallStatement(self, call_statement):
        yield from self.call_statement_body(call_statement)

    def visit_OutputStatement(self, statement):
        format_string = ' '.join('%d' for _ in statement.arguments) + r'\n'
        args = ', '.join(self.visit(v) for v in statement.arguments)
        yield f'System.out.printf("{format_string}", {args});'

    def visit_ReadStatement(self, statement):
        for arg in statement.arguments:
            yield f'{self.visit(arg)} = in.nextInt();'

    def visit_IfStatement(self, statement):
        condition = self.visit(statement.condition)
        yield f'if ({condition})'' {'
        yield from self.block(statement.then_body)
        if statement.else_body is not None:
            yield '} else {'
            yield from self.block(statement.else_body)
        yield '}'

    def visit_ForStatement(self, statement):
        index_name = statement.index.variable.name
        size = self.visit(statement.index.range)
        yield f'for (int {index_name} = 0; {index_name} < {size}; {index_name}++)'' {'
        yield from self.block(statement.body)
        yield '}'

    def visit_LoopStatement(self, loop_statement):
        yield 'while (true) {'
        yield from self.block(loop_statement.body)
        yield '}'

    def build_switch_cases(self, variable, labels):
        variable = self.visit(variable)
        return ' || '.join(f'{variable} == {label}' for label in labels)

    def visit_SwitchStatement(self, switch_statement):
        cases = [case for case in switch_statement.cases]
        yield f'if ({self.build_switch_condition(switch_statement.variable, cases[0].labels)})'' {'
        yield from self.block(cases[0].body)
        for case in cases[1:]:
            yield '}' f' else if ({self.build_switch_condition(switch_statement.variable, case.labels)}) ' '{'
            yield from self.block(case.body)
        yield '}'

    def generate_flush(self):
        yield 'System.out.flush();'

    def visit_ExitStatement(self, exit_statement):
        yield 'System.exit(0);'

    def visit_ReturnStatement(self, return_statement):
        yield f'return {self.visit(return_statement.value)};'

    def visit_BreakStatement(self, break_statement):
        yield 'break;'


class JavaTemplateCodeGen(JavaCodeGen, TemplateCodeGen):
    def generate_header(self, interface):
        yield 'class Solution extends Skeleton {'

    def generate_method_declaration(self, method_declaration):
        if method_declaration.callbacks:
            yield
            yield self.indent(
                self.line_comment(f'interface {self.build_callbacks_interface_name(method_declaration)} ''{'))
            for cbks in method_declaration.callbacks:
                yield self.indent(self.line_comment(self.generate_callbacks_declaration(cbks)))
            yield self.indent(self.line_comment('}'))

        yield
        yield self.indent(f"{self.build_method_signature(method_declaration)}" " {")
        yield self.indent(self.indent('// TODO'))
        if method_declaration.has_return_value:
            yield self.indent(self.indent("return 42;"))
        yield self.indent('}')
