from turingarena.driver.gen.generator import InterfaceCodeGen

class RubyCodeGen(InterfaceCodeGen):
    def visit_Interface(self, n):
        self.line('#!/usr/bin/env ruby')
        self.line("load 'template.rb'")
        self.line()
        for c in n.constants:
            self.visit(c)
            self.line()
        self.line("def main()")
        with self.indent():
            self.visit(n.main)
        self.line("end")
        self.line()
        self.line("main")

    def visit_InterfaceTemplate(self, n):
        for c in n.constants:
            self.visit(c)
            self.line()
        for m in n.methods:
            if m.description:
                for l in m.description:
                    self.line(f"# {l}")
            self.visit(m.prototype)
            with self.indent():
                self.visit(m.body)
            self.line('end')

    def visit_Parameter(self, n):
        return self.visit(n.variable)

    def visit_Callback(self, n):
        params = ", ".join(self.visit(p) for p in n.prototype.parameters)
        self.line(f"def {n.prototype.name}({params})")
        with self.indent():
            self.visit(n.body)

    def visit_Prototype(self, n):
        params = [self.visit(p) for p in n.parameters] + [c.name for c in n.callbacks]
        arguments = ", ".join(params)
        self.line(f'def {n.name}({arguments})')

    def visit_Constant(self, n):
        self.line(f"{self.visit(n.variable)} = {self.visit(n.value)}")

    def visit_Comment(self, n):
        self.line(f"# {n.text}")

    def visit_Read(self, n):
        args = ", ".join(self.visit(a) for a in n.arguments)
        l = "[0]" if len(n.arguments) == 1 else ""
        self.line(f"{args} = gets.split.map(&:to_i){l}")

    def visit_Print(self, n):
        args = ''.join("#{"+str(self.visit(a))+"}" for a in n.arguments)
        self.line(f'puts "{args}"')

    def visit_Call(self, n):
        value_arguments = [self.visit(p) for p in n.arguments]
        callback_arguments = [self.visit(c) for c in n.callbacks]

        parameters = ", ".join(value_arguments + callback_arguments)
        if n.method.has_return_value:
            return_value = f"{self.visit(n.return_value)} = "
        else:
            return_value = ""

        self.line(f"{return_value}{n.method.name}({parameters})")


    def visit_If(self, n):
        condition = self.visit(n.condition)
        headers = [
            f"if {condition}",
            f"else",
        ]
        for header, body in zip(headers, n.branches):
            if body is not None:
                self.line(header)
                with self.indent():
                    self.visit(body)
        self.line("end")

    def visit_For(self, n):
        index_name = n.index.variable.name
        size = self.visit(n.index.range)
        self.line(f"for {index_name} in 0..{size}-1 do")
        with self.indent():
            self.visit(n.body)
        self.line("end")

    def visit_Loop(self, n):
        self.line("while true do")
        with self.indent():
            self.visit(n.body)
        self.line("end")

    def visit_Switch(self, n):
        for i, c in enumerate(n.cases):
            if_or_elsif = "if" if i == 0 else "elsif"
            condition = " or ".join(
                f"{self.visit(n.value)} == {self.visit(l)}"
                for l in c.labels
            )
            self.line(f'{if_or_elsif} {condition}')
            with self.indent():
                self.visit(c.body)
        self.line('end')

    def visit_Exit(self, n):
        self.line('exit')

    def visit_Return(self, n):
        self.line(f"return {self.visit(n.value)}")

    def visit_Break(self, n):
        self.line('break')

    def visit_VariableDeclaration(self, n):
        pass

    def visit_Alloc(self, n):
        reference = self.visit(n.reference)
        size = self.visit(n.size)
        self.line(f"{reference} = Array.new({size})")

    def visit_Flush(self, n):
        self.line("$stdout.flush")
