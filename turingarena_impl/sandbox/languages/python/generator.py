from turingarena_impl.sandbox.languages.generator import CodeGen


class PythonCodeGen(CodeGen):
    @classmethod
    def build_function_declaration(cls, func):
        arguments = ', '.join(p.name for p in func.parameters)
        yield f'def {func.name}({arguments}):'


class PythonSkeletonCodeGen(PythonCodeGen):
    def generate_header(self):
        yield 'import _source'

    def callback_statement(self, callback_statement):
        yield from self.build_function_declaration(callback_statement.callback)
        yield from self.block_content(callback_statement.callback.synthetic_body)

    def main_statement(self, statement):
        yield
        yield 'def main():'
        yield from self.block_content(statement.body)

    def checkpoint_statement(self, checkpoint_statement):
        yield 'print(0)'

    def exit_statement(self, exit_statement):
        yield 'raise SystemExit'

    def break_statement(self, break_statement):
        yield 'break'

    def return_statement(self, return_statement):
        yield f'return {self.expression(return_statement.value)}'

    def generate_flush(self):
        yield f'print(end="", flush=True)'

    def generate_variable_allocation(self, allocated_variable):
        indexes = ''
        for idx in allocated_variable.indexes:
            indexes += f'[{idx}]'

        yield f'{allocated_variable.name}{indexes} = [None] * {allocated_variable.size}'

    def generate_function_declaration(self, function_declaration):
        yield from ()

    def generate_variable_declaration(self, declared_variable):
        yield from ()

    def call_statement(self, call_statement):
        function_name = call_statement.function_name
        parameters = ", ".join(self.expression(p) for p in call_statement.parameters)
        if call_statement.return_value is not None:
            return_value = self.expression(call_statement.return_value)
            yield f'{return_value} = _source.{function_name}({parameters})'
        else:
            yield f'_source.{function_name}({parameters})'

    def write_statement(self, write_statement):
        args = ', '.join(self.expression(arg) for arg in write_statement.arguments)
        yield f'print({args})'

    def read_statement(self, read_statement):
        arguments = ", ".join(self.expression(arg) for arg in read_statement.arguments)
        yield f'[{arguments}] = map(int, input().split())'

    def if_statement(self, if_statement):
        condition = self.expression(if_statement.condition)
        yield f'if {condition}:'
        yield from self.block_content(if_statement.then_body)
        if if_statement.else_body:
            yield 'else:'
            yield from self.block_content(if_statement.else_body)

    def for_statement(self, for_statement):
        index_name = for_statement.index.variable.name
        size = self.expression(for_statement.index.range)
        yield f'for {index_name} in range({size}):'
        yield from self.block_content(for_statement.body)

    def loop_statement(self, loop_statement):
        yield 'while True:'
        yield from self.block_content(loop_statement.body)

    def build_switch_cases(self, variable, labels):
        variable = self.expression(variable)
        return ' or '.join(f'{variable} == {label}' for label in labels)

    def switch_statement(self, switch_statement):
        cases = [case for case in switch_statement.cases]
        yield f'if {self.build_switch_cases(switch_statement.variable, cases[0].labels)}:'
        yield from self.block_content(cases[0].body)
        for case in cases[1:]:
            yield f'elif {self.build_switch_cases(switch_statement.variable, case.labels)}:'
            yield from self.block_content(case.body)


class PythonTemplateCodeGen(PythonCodeGen):
    def generate_function_declaration(self, function_declaration):
        yield
        yield from self.build_function_declaration(function_declaration)
        yield self.indent('pass')

    def generate_main_block(self):
        yield from ()
