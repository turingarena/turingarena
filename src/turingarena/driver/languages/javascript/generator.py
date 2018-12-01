from turingarena.driver.generator import InterfaceCodeGen, SkeletonCodeGen


class JavaScriptCodeGen(InterfaceCodeGen):
    @classmethod
    def build_callable_declarator(cls, callable):
        arguments = ", ".join(cls.visit(p) for p in callable.parameters)
        return f"{callable.name}({arguments})"

    @classmethod
    def visit_ParameterDeclaration(cls, d):
        return f"{d.parameter.name}"


class JavaScriptSkeletonCodeGen(JavaScriptCodeGen, SkeletonCodeGen):
    def generate(self):
        self.line("async function init() {}")
        self.visit(self.interface.body)

    def var_statement(self, statement):
        names = ", ".join(v.name for v in statement.variables)
        self.line(f"let {names};")

    def callback_statement(self, statement):
        callback = statement.callback
        self.line(f"function {build_callable_declarator(callback)}" + "{")
        with self.indent():
            self.visit(callback.body)
        self.line("}")
        self.line()

    def main_statement(self, statement):
        self.line()
        self.line("async function main() {")
        with self.indent():
            self.line("__load_source__(); // load user source file")
            self.visit(statement.body)
        self.line("}")

    def any_statement(self, statement):
        generators = {
            "checkpoint": lambda: ["print(0);"],
            "flush": lambda: ["flush();"],
            "exit": lambda: ["exit(0);"],
            "continue": lambda: ["continue;"],
            "break": lambda: ["break;"],
            "return": lambda: [f"return {self.visit(statement.value)};"],
            "function": lambda: [],
        }
        return generators[statement.statement_type]()

    def visit_Call(self, statement):
        method_name = statement.method.name
        parameters = ", ".join(self.visit(p) for p in statement.arguments)
        if statement.return_value is not None:
            return_value = self.visit(statement.return_value)
            self.line(f"{return_value} = {method_name}({parameters});")
        else:
            self.line(f"{method_name}({parameters});")

    def alloc_statement(self, statement):
        for argument in statement.arguments:
            arg = self.visit(argument)
            size = self.visit(statement.size)
            self.line(f"{arg} = Array({size});")

    def visit_Print(self, statement):
        args = ", ".join(self.visit(v) for v in statement.arguments)
        self.line(f"print({args});")

    def visit_Read(self, statement):
        args = ", ".join(self.visit(arg) for arg in statement.arguments)
        self.line(f"[{args}] = await readIntegers();")

    def visit_If(self, statement):
        condition = self.visit(statement.condition)
        self.line(f"if ({condition})" " {")
        with self.indent():
            self.visit(statement.then_body)
        if statement.else_body is not None:
            self.line("} else {")
            with self.indent():
                self.visit(statement.else_body)
        self.line("}")

    def visit_For(self, statement):
        index_name = statement.index.variable.name
        size = self.visit(statement.index.range)
        self.line(f"for (let {index_name} = 0; {index_name} < {size}; {index_name}++)" " {")
        with self.indent():
            self.visit(statement.body)
        self.line("}")

    def visit_Loop(self, loop_statement):
        self.line("while (true) {")
        with self.indent():
            self.visit(loop_statement.body)
        self.line("}")

    def build_switch_condition(self, variable, labels):
        variable = self.visit(variable)
        result = f"{variable} == {self.visit(labels[0])}"
        for label in labels[1:]:
            result += f" || {variable} == {self.visit(label)}"
        return result

    def visit_Switch(self, switch_statement):
        cases = [case for case in switch_statement.cases]
        self.line(f"if ({self.build_switch_condition(switch_statement.value, cases[0].labels)}) " "{")
        with self.indent():
            self.visit(cases[0].body)
        for case in cases[1:]:
            self.line("}" f" else if ({self.build_switch_condition(switch_statement.value, case.labels)}) " "{")
            with self.indent():
                self.visit(case.body)
        if switch_statement.default:
            self.line("} else {")
            with self.indent():
                self.visit(switch_statement.default)
        self.line("}")


class JavaScriptTemplateCodeGen(JavaScriptCodeGen):
    def visit_MethodPrototype(self, m):
        self.line()
        self.line(f"function {self.build_callable_declarator(m.function)}" + "{")
        with self.indent():
            self.line("// TODO")
        self.line("}")
