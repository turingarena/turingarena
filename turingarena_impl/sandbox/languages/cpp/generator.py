from turingarena_impl.sandbox.languages.generator import CodeGen


class CppCodeGen(CodeGen):
    @classmethod
    def build_callable_declarator(cls, callable):
        return_type = 'int' if callable.return_type else 'void'
        parameters = ', '.join(cls.build_parameter(p) for p in callable.parameters)
        return f"{return_type} {callable.name}({parameters})"

    @staticmethod
    def build_callback_signature(parameter):
        return_type = 'int' if parameter.value_type.has_return_value else "void"
        parameters = ', '.join([f'int {a}' for a in parameter.value_type.arguments])
        return f'{return_type} (*{parameter.name})({parameters})'

    @classmethod
    def build_parameter(cls, parameter):
        if parameter.value_type.meta_type == 'callback':
            return cls.build_callback_signature(parameter)
        else:
            indirections = '*' * parameter.value_type.dimensions if parameter.value_type == 'array' else ''
            return f'int {indirections}{parameter.name}'

    @classmethod
    def build_function_signature(cls, func):
        return_type = 'int' if func.return_type else 'void'
        parameters = ', '.join([cls.build_parameter(p) for p in func.parameters])
        return f'{return_type} {func.name}({parameters})'


class CppSkeletonCodeGen(CppCodeGen):
    def generate_header(self):
        yield "#include <cstdio>"
        yield "#include <cstdlib>"
        yield

    def callback_statement(self, s):
        callback = s.callback
        parameters = ', '.join(f'int {p.name}' for p in callback.parameters)
        return_value = '-> int' if callback.return_type else ''
        yield f"auto {callback.name} = []({parameters}) {return_value}" " {"
        yield from self.block_content(callback.synthetic_body)
        yield "}"

    def function_declaration(self, s):
        yield f"{self.build_function_signature(s)};"

    def generate_main(self):
        yield
        yield "int main() {"
        yield from self.block_content(self.interface.main)
        yield "}"

    def call_statement(self, s):
        function_name = s.function.name
        parameters = ", ".join(self.expression(p) for p in s.parameters)
        if s.return_value is not None:
            return_value = self.expression(s.return_value)
            yield f"int {return_value} = {function_name}({parameters});"
        else:
            yield f"{function_name}({parameters});"

    def write_statement(self, s):
        format_string = ' '.join("%d" for _ in s.arguments) + r'\n'
        args = ', '.join(self.expression(v) for v in s.arguments)
        yield f'printf("{format_string}", {args});'

    def read_statement(self, statement):
        format_string = ''.join("%d" for _ in statement.arguments)
        scanf_args = ', '.join("&" + self.expression(v) for v in statement.arguments)
        variables = ', '.join(self.expression(v) for v in statement.arguments)
        yield f'static int {variables};'  # TODO: array allocation
        yield f'fflush(stdout);'
        yield f'scanf("{format_string}", {scanf_args});'

    def if_statement(self, s):
        condition = self.expression(s.condition)
        yield f"if( {condition} )" " {"
        yield from self.block_content(s.then_body)
        yield "}"
        if s.else_body is not None:
            yield "else {"
            yield from self.block_content(s.else_body)
            yield "}"

    def for_statement(self, s):
        index_name = s.index.variable.name
        size = self.expression(s.index.range)
        yield f"for(int {index_name} = 0; {index_name} < {size}; {index_name}++)" " {"
        yield from self.block_content(s.body)
        yield "}"

    def loop_statement(self, s):
        yield "while (true) {"
        yield from self.block_content(s.body)
        yield "}"

    def build_switch_condition(self, variable, labels):
        variable = self.expression(variable)
        result = f"{variable} == {self.expression(labels[0])}"
        for label in labels[1:]:
            result += f" || {variable} == {self.expression(label)}"
        return result

    def switch_statement(self, s):
        cases = [case for case in s.cases]
        yield f"if ({self.build_switch_condition(s.variable, cases[0].labels)}) " "{"
        yield from self.block_content(cases[0].body)
        for case in cases[1:]:
            yield "}" f" else if ({self.build_switch_condition(s.variable, case.labels)}) " "{"
            yield from self.block_content(case.body)
        if s.default:
            yield "} else {"
            yield from self.block_content(s.default)
        yield "}"

    def any_statement(self, s):
        generators = {
            "checkpoint": lambda: [r"""printf("%d\n", 0);"""],
            "exit": lambda: ["exit(0);"],
            "continue": lambda: ["continue;"],
            "break": lambda: ["break;"],
            "return": lambda: [f"return {self.expression(s.value)};"],
        }
        return generators[s.statement_type]()


class CppTemplateCodeGen(CppCodeGen):
    def function_declaration(self, s):
        yield
        yield f"{self.build_callable_declarator(s.function)}" " {"
        yield self.indent("// TODO")
        yield "}"
