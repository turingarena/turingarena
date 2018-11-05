from turingarena.driver.generator import InterfaceCodeGen, SkeletonCodeGen


class JavaScriptCodeGen(InterfaceCodeGen):
    @classmethod
    def build_callable_declarator(cls, callable):
        arguments = ", ".join(cls.build_parameter(p) for p in callable.parameters)
        return f"{callable.name}({arguments})"

    @classmethod
    def build_parameter(cls, parameter):
        return f"{parameter.name}"


class JavaScriptSkeletonCodeGen(JavaScriptCodeGen, SkeletonCodeGen):
    def generate(self):
        yield "async function init() {}"
        yield from self.block(self.interface.body)

    def var_statement(self, statement):
        names = ", ".join(v.name for v in statement.variables)
        yield f"let {names};"

    def callback_statement(self, statement):
        callback = statement.callback
        yield f"function {build_callable_declarator(callback)}" + "{"
        yield from self.block(callback.synthetic_body)
        yield "}"
        yield

    def main_statement(self, statement):
        yield
        yield "async function main() {"
        yield self.indent("__load_source__(); // load user source file")
        yield from self.block(statement.body)
        yield "}"

    def any_statement(self, statement):
        generators = {
            "checkpoint": lambda: ["print(0);"],
            "flush": lambda: ["flush();"],
            "exit": lambda: ["exit(0);"],
            "continue": lambda: ["continue;"],
            "break": lambda: ["break;"],
            "return": lambda: [f"return {self.expression(statement.value)};"],
            "function": lambda: [],
        }
        return generators[statement.statement_type]()

    def call_statement(self, statement):
        method_name = statement.method.name
        parameters = ", ".join(self.expression(p) for p in statement.parameters)
        if statement.return_value is not None:
            return_value = self.expression(statement.return_value)
            yield f"{return_value} = {method_name}({parameters});"
        else:
            yield f"{method_name}({parameters});"

    def alloc_statement(self, statement):
        for argument in statement.arguments:
            arg = self.expression(argument)
            size = self.expression(statement.size)
            yield f"{arg} = Array({size});"

    def write_statement(self, statement):
        args = ", ".join(self.expression(v) for v in statement.arguments)
        yield f"print({args});"

    def read_statement(self, statement):
        args = ", ".join(self.expression(arg) for arg in statement.arguments)
        yield f"[{args}] = await readIntegers();"

    def if_statement(self, statement):
        condition = self.expression(statement.condition)
        yield f"if ({condition})" " {"
        yield from self.block(statement.then_body)
        if statement.else_body is not None:
            yield "} else {"
            yield from self.block(statement.else_body)
        yield "}"

    def for_statement(self, statement):
        index_name = statement.index.variable.name
        size = self.expression(statement.index.range)
        yield f"for (let {index_name} = 0; {index_name} < {size}; {index_name}++)" " {"
        yield from self.block(statement.body)
        yield "}"

    def loop_statement(self, loop_statement):
        yield "while (true) {"
        yield from self.block(loop_statement.body)
        yield "}"

    def build_switch_condition(self, variable, labels):
        variable = self.expression(variable)
        result = f"{variable} == {self.expression(labels[0])}"
        for label in labels[1:]:
            result += f" || {variable} == {self.expression(label)}"
        return result

    def switch_statement(self, switch_statement):
        cases = [case for case in switch_statement.cases]
        yield f"if ({self.build_switch_condition(switch_statement.variable, cases[0].labels)}) " "{"
        yield from self.block(cases[0].body)
        for case in cases[1:]:
            yield "}" f" else if ({self.build_switch_condition(switch_statement.variable, case.labels)}) " "{"
            yield from self.block(case.body)
        if switch_statement.default:
            yield "} else {"
            yield from self.block(switch_statement.default)
        yield "}"


class JavaScriptTemplateCodeGen(JavaScriptCodeGen):
    def generate_method_declaration(self, method_declaration):
        yield
        yield f"function {self.build_callable_declarator(method_declaration.function)}" + "{"
        yield self.indent("// TODO")
        yield "}"
