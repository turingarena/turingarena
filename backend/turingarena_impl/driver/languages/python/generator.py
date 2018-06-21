from turingarena_impl.driver.generator import SkeletonCodeGen, InterfaceCodeGen, TemplateCodeGen


class PythonCodeGen(InterfaceCodeGen):
    def build_method_declaration(self, func):
        arguments = ', '.join(p.name for p in func.parameters)
        yield f'def {func.name}({arguments}):'

    def line_comment(self, comment):
        return f"# {comment}"


class PythonSkeletonCodeGen(PythonCodeGen, SkeletonCodeGen):
    def generate_header(self, interface):
        yield 'from _source import *'

    def callback_statement(self, callback_statement):
        yield from self.build_method_declaration(callback_statement.callback)
        yield from self.block(callback_statement.callback.synthetic_body)

    def main_statement(self, statement):
        yield
        yield 'def main():'
        yield from self.block(statement.body)

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

    def generate_variable_allocation(self, variable, indexes, size):
        indexes = "".join(f"[{idx.variable.name}]" for idx in indexes)
        size = self.expression(size)
        yield f"{variable.name}{indexes} = [None] * {size}"

    def generate_method_declaration(self, method_declaration):
        yield from ()

    def generate_variable_declaration(self, declared_variable):
        yield from ()

    def generate_callback(self, callback):
        params = ", ".join(parameter.name for parameter in callback.parameters)
        yield f"def _callback_{callback.name}({params}):"
        yield from self.block(callback.synthetic_body)

    def call_statement(self, call_statement):
        method_name = call_statement.method_name

        for callback in call_statement.callbacks:
            yield from self.generate_callback(callback)

        value_arguments = [self.expression(p) for p in call_statement.arguments]
        callback_arguments = [
            f"_callback_{callback.name}"
            for callback in call_statement.callbacks
        ]
        arguments = ", ".join(value_arguments + callback_arguments)
        if call_statement.return_value is not None:
            return_value = self.expression(call_statement.return_value)
            yield f'{return_value} = {method_name}({arguments})'
        else:
            yield f'{method_name}({arguments})'

    def write_statement(self, write_statement):
        args = ', '.join(self.expression(arg) for arg in write_statement.arguments)
        yield f'print({args})'

    def read_statement(self, read_statement):
        arguments = ", ".join(self.expression(arg) for arg in read_statement.arguments)
        yield f'[{arguments}] = map(int, input().split())'

    def if_statement(self, if_statement):
        condition = self.expression(if_statement.condition)
        yield f'if {condition}:'
        yield from self.block(if_statement.then_body)
        if if_statement.else_body:
            yield 'else:'
            yield from self.block(if_statement.else_body)

    def for_statement(self, for_statement):
        index_name = for_statement.index.variable.name
        size = self.expression(for_statement.index.range)
        yield f'for {index_name} in range({size}):'
        yield from self.block(for_statement.body)

    def loop_statement(self, loop_statement):
        yield 'while True:'
        yield from self.block(loop_statement.body)

    def build_switch_cases(self, variable, labels):
        variable = self.expression(variable)
        return ' or '.join(f'{variable} == {label}' for label in labels)

    def switch_statement(self, switch_statement):
        cases = [case for case in switch_statement.cases]
        yield f'if {self.build_switch_cases(switch_statement.variable, cases[0].labels)}:'
        yield from self.block(cases[0].body)
        for case in cases[1:]:
            yield f'elif {self.build_switch_cases(switch_statement.variable, case.labels)}:'
            yield from self.block(case.body)


class PythonTemplateCodeGen(PythonCodeGen, TemplateCodeGen):
    def generate_method_declaration(self, method_declaration):
        yield
        yield from self.build_method_declaration(method_declaration)
        yield self.indent('pass')
