from turingarena.driver.gen.generator import InterfaceCodeGen

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
    def visit_Interface(self, n):
        self.line('import os as _os')
        self.line()
        for c in n.constants:
            self.visit(c)
            self.line()
        self.line('def main(_solution):')
        with self.indent():
            self.visit(n.main)
        self.line()
        self.line(SKELETON_REAL_MAIN)

    def visit_Prototype(self, func):
        arguments = ', '.join(
            [self.visit(p) for p in func.parameters] +
            [c.name for c in func.callbacks]
        )
        self.line(f'def {func.name}({arguments}):')

    def visit_Parameter(self, n):
        return self.visit(n.variable)

    def visit_Constant(self, n):
        self.line(f"{n.variable.name} = {self.visit(n.value)}")

    def visit_Comment(self, n):
        self.line(f"# {n.text}")

    def visit_Exit(self, n):
        self.visit_Flush(None)
        self.line('_os._exit(0)')

    def visit_Break(self, n):
        self.line('break')

    def visit_Return(self, n):
        self.line(f'return {self.visit(n.value)}')

    def visit_Flush(self, n):
        self.line(f'print(end="", flush=True)')

    def visit_Alloc(self, n):
        size = self.visit(n.size)
        self.line(f"{self.visit(n.reference)} = [None] * {size}")

    def visit_VariableDeclaration(self, n):
        pass

    def visit_Callback(self, n):
        params = ", ".join(self.visit(p) for p in n.prototype.parameters)
        self.line(f"def _callback_{n.prototype.name}({params}):")
        with self.indent():
            self.visit(n.body)

    def visit_Call(self, n):
        method_name = n.method.name

        for callback in n.callbacks:
            self.visit_Callback(callback)

        value_arguments = [self.visit(p) for p in n.arguments]
        callback_arguments = [
            f"_callback_{c.prototype.name}"
            for c in n.callbacks
        ]
        arguments = ", ".join(value_arguments + callback_arguments)
        call_expr = f"_solution.{method_name}({arguments})"
        if n.return_value is not None:
            return_value = self.visit(n.return_value)
            return_expr = f"{return_value} = "
        else:
            return_expr = ""
        self.line(f"{return_expr}{call_expr}")

    def visit_Print(self, n):
        args = ', '.join(self.visit(arg) for arg in n.arguments)
        self.line(f'print({args})')

    def visit_Read(self, n):
        arguments = ", ".join(self.visit(arg) for arg in n.arguments)
        self.line(f'[{arguments}] = map(int, input().split())')

    def visit_If(self, n):
        condition = self.visit(n.condition)
        headers = [
            f"if {condition}:",
            f"else:"
        ]
        for header, body in zip(headers, n.branches):
            if body is not None:
                self.line(header)
                with self.indent():
                    self.visit(body)

    def visit_For(self, n):
        index_name = n.index.variable.name
        size = self.visit(n.index.range)
        self.line(f'for {index_name} in range({size}):')
        with self.indent():
            self.visit(n.body)

    def visit_Loop(self, n):
        self.line('while True:')
        with self.indent():
            self.visit(n.body)

    def visit_Switch(self, n):
        for i, c in enumerate(n.cases):
            if_or_elif = "if" if i == 0 else "elif"
            condition = " or ".join(
                f"{self.visit(n.value)} == {self.visit(l)}"
                for l in c.labels
            )
            self.line(f'{if_or_elif} {condition}:')
            with self.indent():
                self.visit(c.body)

    def visit_InterfaceTemplate(self, n):
        for m in n.methods:
            self.visit(m)
            self.line()

    def visit_MethodTemplate(self, n):
        if n.description:
            for l in n.description.splitlines():
                self.line(f"# {l}")
        self.visit(n.prototype)
        with self.indent():
            self.visit(n.body)
            self.line(f"pass")
