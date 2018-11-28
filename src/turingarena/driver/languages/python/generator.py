from turingarena.driver.generator import SkeletonCodeGen, InterfaceCodeGen, TemplateCodeGen

SKELETON_REAL_MAIN = r"""
if __name__ == '__main__':
    import sys
    import runpy
    
    if len(sys.argv) != 2:
        print("Usage: {} <solution>".format(sys.argv[0]))
    
    class Wrapper: pass 
    solution = Wrapper()
    solution.__dict__ = runpy.run_path(sys.argv[1])
    main(solution)
"""


class PythonCodeGen(InterfaceCodeGen):
    def build_method_declaration(self, func):
        arguments = ', '.join([p.name for p in func.parameters] + [c.name for c in func.callbacks])
        yield f'def {func.name}({arguments}):'

    def visit_ConstantDeclaration(self, m):
        yield f"{m.variable.name} = {self.visit(m.value)}"

    def line_comment(self, comment):
        return f"# {comment}"


class PythonSkeletonCodeGen(PythonCodeGen, SkeletonCodeGen):
    def generate_header(self, interface):
        yield 'import os as _os'
        yield

    def generate_footer(self, interface):
        yield
        yield SKELETON_REAL_MAIN

    def callback_statement(self, callback_statement):
        yield from self.build_method_declaration(callback_statement.callback)
        with self.indent():
            yield from self.visit(callback_statement.callback.body)

    def generate_main_block(self, interface):
        yield
        yield 'def main(_solution):'
        with self.indent():
            yield from self.visit(interface.main_block)

    def visit_Exit(self, exit_statement):
        yield from self.generate_flush()
        yield '_os._exit(0)'

    def visit_Break(self, break_statement):
        yield 'break'

    def visit_Return(self, return_statement):
        yield f'return {self.visit(return_statement.value)}'

    def generate_flush(self):
        yield f'print(end="", flush=True)'

    def visit_ReferenceAllocation(self, a):
        name = a.reference.variable.name
        indexes = "".join(f"[{idx.name}]" for idx in a.reference.indexes)
        size = self.visit(a.size)
        yield f"{name}{indexes} = [None] * {size}"

    def visit_MethodPrototype(self, m):
        yield from ()

    def visit_VariableDeclaration(self, d):
        yield from ()

    def generate_callback(self, callback):
        params = ", ".join(parameter.name for parameter in callback.parameters)
        yield f"def _callback_{callback.name}({params}):"
        with self.indent():
            yield from self.visit(callback.body)

    def visit_Call(self, call_statement):
        method_name = call_statement.method_name

        for callback in call_statement.callbacks:
            yield from self.generate_callback(callback)

        value_arguments = [self.visit(p) for p in call_statement.arguments]
        callback_arguments = [
            f"_callback_{callback.name}"
            for callback in call_statement.callbacks
        ]
        arguments = ", ".join(value_arguments + callback_arguments)
        call_expr = f"_solution.{method_name}({arguments})"
        if call_statement.return_value is not None:
            return_value = self.visit(call_statement.return_value)
            yield f'{return_value} = {call_expr}'
        else:
            yield f'{call_expr}'

    def visit_Print(self, write_statement):
        args = ', '.join(self.visit(arg) for arg in write_statement.arguments)
        yield f'print({args})'

    def visit_Read(self, read_statement):
        arguments = ", ".join(self.visit(arg) for arg in read_statement.arguments)
        yield f'[{arguments}] = map(int, input().split())'

    def visit_If(self, if_statement):
        condition = self.visit(if_statement.condition)
        yield f'if {condition}:'
        with self.indent():
            yield from self.visit(if_statement.then_body)
        if if_statement.else_body:
            yield 'else:'
            with self.indent():
                yield from self.visit(if_statement.else_body)

    def visit_For(self, for_statement):
        index_name = for_statement.index.variable.name
        size = self.visit(for_statement.index.range)
        yield f'for {index_name} in range({size}):'
        with self.indent():
            yield from self.visit(for_statement.body)

    def visit_Loop(self, loop_statement):
        yield 'while True:'
        with self.indent():
            yield from self.visit(loop_statement.body)

    def build_switch_cases(self, variable, labels):
        variable = self.visit(variable)
        return ' or '.join(f'{variable} == {label}' for label in labels)

    def visit_Switch(self, switch_statement):
        cases = [case for case in switch_statement.cases]
        yield f'if {self.build_switch_cases(switch_statement.variable, cases[0].labels)}:'
        with self.indent():
            yield from self.visit(cases[0].body)
        for case in cases[1:]:
            yield f'elif {self.build_switch_cases(switch_statement.variable, case.labels)}:'
            with self.indent():
                yield from self.visit(case.body)


class PythonTemplateCodeGen(PythonCodeGen, TemplateCodeGen):
    def visit_MethodPrototype(self, m):
        yield
        yield from self.build_method_declaration(m)
        with self.indent():
            if m.has_return_value:
                yield "return 42"
            else:
                yield 'pass'
