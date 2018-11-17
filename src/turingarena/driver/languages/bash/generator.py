from turingarena.driver.generator import InterfaceCodeGen, SkeletonCodeGen, TemplateCodeGen


class BashCodeGen(InterfaceCodeGen):
    def line_comment(self, comment):
        return f"# {comment}"

    def generate_constant_declaration(self, name, value):
        yield f"{name}={value}"


class BashSkeletonCodeGen(BashCodeGen, SkeletonCodeGen):

    def generate_header(self, interface):
        yield "#!/usr/bin/env bash"
        yield
        yield "source solution.sh"
        yield

    def visit_ReadStatement(self, read_statement):
        for i in range(len(read_statement.arguments) - 1):
            yield f"read -d ' ' {self.visit(read_statement.arguments[i])}"
        yield f"read {self.visit(read_statement.arguments[i + 1])}"

    def visit_OutputStatement(self, write_statement):
        for arg in write_statement.arguments:
            yield f"echo -n $(({self.visit(arg)}))"
        yield "echo"

    def visit_IfStatement(self, if_statement):
        condition = self.visit(if_statement.condition)
        yield f"if (({condition})); then"
        yield from self.indent_all(self.visit(if_statement.then_body))
        if if_statement.else_body:
            yield "else"
            yield from self.indent_all(self.visit(if_statement.else_body))
        yield "fi"

    def visit_ForStatement(self, for_statement):
        index = for_statement.index.variable.name
        size = self.visit(for_statement.index.range)
        yield f"for (({index}=0; index<{size}; i++)); do"
        yield self.indent_all(self.visit(for_statement.body))
        yield "done"

    def visit_LoopStatement(self, loop_statement):
        yield "while true; do"
        yield self.indent_all(self.visit(loop_statement.body))
        yield "done"

    def visit_BreakStatement(self, break_statement):
        yield "break"

    def visit_ReturnStatement(self, return_statement):
        yield f"_return_val={self.visit(return_statement.value)}"

    def visit_ExitStatement(self, exit_statement):
        yield 'exit'

    def generate_flush(self):
        yield from ()

    def visit_CallStatement(self, call_statement):
        arguments = " ".join(f"$(({self.visit(p)}))" for p in call_statement.arguments)
        yield f"{call_statement.method_name} {arguments}"
        if call_statement.return_value is not None:
            return_value = self.visit(call_statement.return_value)
            yield f"{return_value}=$return_val"

    def visit_SwitchStatement(self, switch_statement):
        pass

    def visit_VariableAllocation(self, a):
        # FIXME: not implemented
        pass

    def visit_MethodPrototype(self, m):
        yield from ()

    def visit_VariableDeclaration(self, d):
        yield from ()


class BashTemplateCodeGen(BashCodeGen, TemplateCodeGen):
    def visit_MethodPrototype(self, m):
        arguments = [p.name for p in m.parameters]
        yield f"function {m.name} " "{"
        for i, arg in enumerate(arguments):
            yield self.indent(f"{arg}=${i+1}")
        yield self.indent(self.line_comment("TODO"))
        yield "}"
