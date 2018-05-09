from turingarena_impl.sandbox.languages.generator import CodeGen


class PythonCodeGen(CodeGen):
    @classmethod
    def generate_globals(cls, context):
        if context.global_variables:
            variables = ", ".join(v.name for v in context.global_variables)
            yield f"global {variables}"

    @classmethod
    def build_callable_declarator(cls, callable):
        arguments = ', '.join(cls.build_parameter(p) for p in callable.parameters)
        return f"{callable.name}({arguments})"

    @classmethod
    def build_parameter(cls, parameter):
        return f'{parameter.name}'

    @classmethod
    def build_type(cls, t):
        builders = {
            "scalar": lambda: f"int",
            "array": lambda: f"List[{cls.build_type(t.item_type)}]",
        }
        return builders[t.meta_type]()


class PythonSkeletonCodeGen(PythonCodeGen):
    def generate(self):
        yield from self.block_content(self.interface.body, indent=False)
        yield
        yield "import source as _source"

    def var_statement(self, statement):
        names = ", ".join(d.name for d in statement.variables)
        formats = ", ".join(self.build_type(d.value_type) for d in statement.variables)
        yield f"# {names} : {formats}"

    def callback_statement(self, statement):
        callback = statement.callback
        yield f"def {self.build_callable_declarator(callback)}:"
        yield from self.indent_all(self.generate_globals(statement.context))
        yield from self.block_content(callback.synthetic_body)

    def init_statement(self, statement):
        yield
        yield "# init block"
        yield from self.block_content(statement.body, indent=False)

    def main_statement(self, statement):
        yield
        yield 'def main():'
        yield from self.indent_all(self.generate_globals(statement.context))
        yield from self.block_content(statement.body)

    def any_statement(self, statement):
        generators = {
            "checkpoint": lambda: ["""print(0)"""],
            "flush": lambda: ["""print(end="", flush=True)"""],
            "exit": lambda: ["raise SystemExit"],
            "continue": lambda: ["continue"],
            "break": lambda: ["break"],
            "return": lambda: [f"return {self.expression(statement.value)}"],
            "function": lambda: [],
        }
        return generators[statement.statement_type]()

    def alloc_statement(self, statement):
        for argument in statement.arguments:
            arg = self.expression(argument)
            size = self.expression(statement.size)
            yield f"{arg} = [None] * {size}"

    def call_statement(self, statement):
        function_name = statement.function_name
        parameters = ", ".join(self.expression(p) for p in statement.parameters)
        if statement.return_value is not None:
            return_value = self.expression(statement.return_value)
            yield f"{return_value} = _source.{function_name}({parameters})"
        else:
            yield f"_source.{function_name}({parameters})"

    def write_statement(self, statement):
        args = ', '.join(self.expression(v) for v in statement.arguments)
        yield f'print({args})'

    def read_statement(self, statement):
        arguments = ", ".join(
            self.expression(v)
            for v in statement.arguments
        )

        yield f"[{arguments}] = map(int, input().split())"

    def if_statement(self, statement):
        condition = self.expression(statement.condition)
        yield f"if {condition}:"
        yield from self.block_content(statement.then_body)
        if statement.else_body:
            yield "else:"
            yield from self.block_content(statement.else_body)

    def for_statement(self, statement):
        index_name = statement.index.variable.name
        size = self.expression(statement.index.range)
        yield f"for {index_name} in range({size}):"
        yield from self.block_content(statement.body)

    def loop_statement(self, s):
        yield "while True:"
        yield from self.block_content(s.body)

    def build_switch_cases(self, variable, labels):
        variable = self.expression(variable)
        result = f"{variable} == {self.expression(labels[0])}"
        for label in labels[1:]:
            result += f" or {variable} == {self.expression(label)}"
        return result

    def switch_statement(self, s):
        cases = [case for case in s.cases]
        yield f"if {self.build_switch_cases(s.variable, cases[0].labels)}:"
        yield from self.block_content(cases[0].body)

        for case in cases[1:]:
            yield f"elif {self.build_switch_cases(s.variable, case.labels)}:"
            yield from self.block_content(case.body)

        if s.default:
            yield "else:"
            yield from self.block_content(s.default)


class PythonTemplateCodeGen(PythonCodeGen):
    def generate_function_declaration(self, statement):
        yield
        yield f"def {self.build_callable_declarator(statement.function)}:"
        yield self.indent("# TODO")
        yield self.indent("pass")
