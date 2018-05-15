from turingarena_impl.sandbox.languages.generator import CodeGen


class CppCodeGen(CodeGen):
    @staticmethod
    def build_callback_signature(parameter):
        return_type = 'int' if parameter.value_type.has_return_value else "void"
        parameters = ', '.join([f'int {a}' for a in parameter.value_type.arguments])
        return f'{return_type} {parameter.name}({parameters})'

    @classmethod
    def build_parameter(cls, parameter):
        if parameter.value_type.meta_type == 'callback':
            return cls.build_callback_signature(parameter)
        else:
            indirections = '*' * parameter.value_type.dimensions if parameter.value_type.meta_type == 'array' else ''
            return f'int {indirections}{parameter.name}'

    @classmethod
    def build_function_signature(cls, func):
        return_type = 'int' if func.has_return_value else 'void'
        parameters = ', '.join([cls.build_parameter(p) for p in func.parameters])
        return f'{return_type} {func.name}({parameters})'


class CppSkeletonCodeGen(CppCodeGen):
    def generate_header(self):
        yield "#include <cstdio>"
        yield

    def generate_variable_declaration(self, declared_variable):
        yield f"static int {'*' * declared_variable.dimensions}{declared_variable.name};"

    def generate_variable_allocation(self, allocated_variable):
        indexes = ""
        for idx in allocated_variable.indexes:
            indexes += f"[{idx}]"
        yield f"{allocated_variable.name}{indexes} = new int{'*' * allocated_variable.dimensions}[{allocated_variable.size}];"

    def callback_statement(self, callback_statement):
        callback = callback_statement.callback
        parameters = ', '.join(f'int {p.name}' for p in callback.parameters)
        return_value = ' -> int' if callback.return_type else ''
        yield f"auto {callback.name} = []({parameters}){return_value}" " {"
        yield from self.block_content(callback.synthetic_body)
        yield "};"

    def generate_function_declaration(self, s):
        yield f"{self.build_function_signature(s)};"

    def generate_main_block(self):
        yield
        yield "int main() {"
        yield from self.block_content(self.interface.main)
        yield "}"

    def call_statement(self, call_statement):
        function_name = call_statement.function.name
        parameters = ", ".join(self.expression(p) for p in call_statement.parameters)
        if call_statement.return_value is not None:
            return_value = self.expression(call_statement.return_value)
            yield f"{return_value} = {function_name}({parameters});"
        else:
            yield f"{function_name}({parameters});"

    def write_statement(self, write_statement):
        format_string = ' '.join("%d" for _ in write_statement.arguments) + r'\n'
        args = ', '.join(self.expression(v) for v in write_statement.arguments)
        yield f'printf("{format_string}", {args});'

    def read_statement(self, statement):
        format_string = ''.join("%d" for _ in statement.arguments)
        scanf_args = ', '.join("&" + self.expression(v) for v in statement.arguments)
        yield f'scanf("{format_string}", {scanf_args});'

    def if_statement(self, statement):
        condition = self.expression(statement.condition)
        yield f"if ({condition})" " {"
        yield from self.block_content(statement.then_body)
        if s.else_body:
            yield "} else {"
            yield from self.block_content(statement.else_body)
        yield "}"

    def for_statement(self, s):
        index_name = s.index.variable.name
        size = self.expression(s.index.range)
        yield f"for (int {index_name} = 0; {index_name} < {size}; {index_name}++)" " {"
        yield from self.block_content(s.body)
        yield "}"

    def loop_statement(self, statement):
        yield "while (true) {"
        yield from self.block_content(statement.body)
        yield "}"

    def build_switch_cases(self, variable, labels):
        variable = self.expression(variable)
        return ' || '.join(f'{variable} == {label}' for label in labels)

    def switch_statement(self, statement):
        cases = [case for case in statement.cases]
        yield f"if ({self.build_switch_condition(statement.variable, cases[0].labels)}) " "{"
        yield from self.block_content(cases[0].body)
        for case in cases[1:]:
            yield "}" f" else if ({self.build_switch_condition(statement.variable, case.labels)}) " "{"
            yield from self.block_content(case.body)
        yield "}"

    def checkpoint_statement(self, statement):
        yield 'puts("0");'

    def exit_statement(self, statement):
        yield 'exit(0);'

    def return_statement(self, statement):
        yield f'return {self.expression(statement.value)};'

    def break_statement(self, statement):
        yield 'break;'

    def generate_flush(self):
        yield 'fflush(stdout);'


class CppTemplateCodeGen(CppCodeGen):
    def generate_function_declaration(self, s):
        yield
        yield f"{self.build_function_signature(s.signature)}" " {"
        yield self.indent("// TODO")
        yield "}"

    def generate_main_block(self):
        yield from ()
