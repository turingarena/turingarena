from turingarena.driver.gen.generator import InterfaceCodeGen


class BashCodeGen(InterfaceCodeGen):
    def visit_Comment(self, n):
        self.line(f"# {n.text}")

    def visit_Constant(self, m):
        self.line(f"{m.variable.name}={self.visit(m.value)}")

    def generate_header(self, interface):
        self.line("#!/usr/bin/env bash")
        self.line()
        self.line("source solution.sh")
        self.line()

    def visit_Read(self, read_statement):
        for i in range(len(read_statement.arguments) - 1):
            self.line(f"read -d ' ' {self.visit(read_statement.arguments[i])}")
        self.line(f"read {self.visit(read_statement.arguments[i + 1])}")

    def visit_Print(self, write_statement):
        for arg in write_statement.arguments:
            self.line(f"echo -n $(({self.visit(arg)}))")
        self.line("echo")

    def visit_If(self, if_statement):
        condition = self.visit(if_statement.condition)
        self.line(f"if (({condition})); then")
        with self.indent():
            self.visit(if_statement.branches.then_body)
        if if_statement.branches.else_body:
            self.line("else")
            with self.indent():
                self.visit(if_statement.branches.else_body)
        self.line("fi")

    def visit_For(self, for_statement):
        index = for_statement.index.variable.name
        size = self.visit(for_statement.index.range)
        self.line(f"for (({index}=0; index<{size}; i++)); do")
        with self.indent():
            self.visit(for_statement.body)
        self.line("done")

    def visit_Loop(self, loop_statement):
        self.line("while true; do")
        with self.indent():
            self.visit(loop_statement.body)
        self.line("done")

    def visit_Break(self, break_statement):
        self.line("break")

    def visit_Return(self, return_statement):
        self.line(f"_return_val={self.visit(return_statement.value)}")

    def visit_Exit(self, exit_statement):
        self.line('exit')

    def visit_Flush(self, n):
        pass

    def visit_Call(self, call_statement):
        arguments = " ".join(f"$(({self.visit(p)}))" for p in call_statement.arguments)
        self.line(f"{call_statement.method.name} {arguments}")
        if call_statement.return_value is not None:
            return_value = self.visit(call_statement.return_value)
            self.line(f"{return_value}=$return_val")

    def visit_Switch(self, switch_statement):
        pass

    def visit_ReferenceAllocation(self, a):
        # FIXME: not implemented
        pass

    def method_declaration(self, m):
        pass

    def visit_VariableDeclaration(self, d):
        pass

    def method_declaration(self, m):
        arguments = [p.variable.name for p in m.parameters]
        self.line(f"function {m.name} " "{")
        with self.indent():
            for i, arg in enumerate(arguments):
                self.line(f"{arg}=${i+1}")
            self.line_comment("TODO")
        self.line("}")
