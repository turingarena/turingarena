from turingarena.interface.context import StaticGlobalContext
from turingarena.sandbox.languages.generator import CodeGen


class CppCodeGen(CodeGen):
    @classmethod
    def generate_declarators(cls, declaration):
        for variable in declaration.variables:
            yield cls.build_declarator(declaration.value_type, variable.name)

    @classmethod
    def build_callable_declarator(cls, callable):
        return_type = cls.build_full_type(callable.return_type)
        parameters = ', '.join(cls.build_parameter(p) for p in callable.parameters)
        return f"{return_type} {callable.name}({parameters})"

    @classmethod
    def build_declaration(cls, statement):
        type_specifier = cls.build_type_specifier(statement.value_type)
        declarators = ', '.join(cls.generate_declarators(statement))
        return f'{type_specifier} {declarators};'

    @classmethod
    def build_parameter(cls, parameter):
        full_type = cls.build_full_type(parameter.value_type)
        return f'{full_type} {parameter.name}'

    @classmethod
    def build_declarator(cls, value_type, name):
        if value_type is None:
            return name
        builders = {
            "scalar": lambda: name,
            "array": lambda: "*" + cls.build_declarator(value_type.item_type, name),
        }
        return builders[value_type.meta_type]()

    @classmethod
    def build_type_specifier(cls, value_type):
        if value_type is None:
            return "void"
        builders = {
            "scalar": lambda: {
                int: "int",
            }[value_type.base_type],
            "array": lambda: cls.build_type_specifier(value_type.item_type)
        }
        return builders[value_type.meta_type]()

    @classmethod
    def build_full_type(cls, value_type):
        return cls.build_type_specifier(value_type) + cls.build_declarator(value_type, "")


class CppSkeletonCodeGen(CppCodeGen):
    def generate(self):
        yield "#include <cstdio>"
        yield "#include <cstdlib>"
        yield from self.block_content(self.interface.body, indent=False)

    def var_statement(self, s):
        if isinstance(s.context, StaticGlobalContext):
            yield "extern " + self.build_declaration(s)
        else:
            yield self.build_declaration(s)

    def callback_statement(self, s):
        callback = s.callback
        yield f"{self.build_callable_declarator(callback)}" " {"
        yield from self.block_content(callback.synthetic_body)
        yield "}"

    def function_statement(self, s):
        yield f"{self.build_callable_declarator(s.function)};"

    def init_statement(self, s):
        yield
        yield "__attribute__((constructor)) static void init() {"
        yield from self.block_content(s.body)
        yield "}"

    def main_statement(self, s):
        yield
        yield "int main() {"
        yield from self.block_content(s.body)
        yield "}"

    def alloc_statement(self, s):
        for argument in s.arguments:
            arg = self.expression(argument)
            value_type = self.build_full_type(argument.value_type.item_type)
            size = self.expression(s.size)
            yield f"{arg} = new {value_type}[{size}];"

    def call_statement(self, s):
        function_name = s.function.name
        parameters = ", ".join(self.expression(p) for p in s.parameters)
        if s.return_value is not None:
            return_value = self.expression(s.return_value)
            yield f"{return_value} = {function_name}({parameters});"
        else:
            yield f"{function_name}({parameters});"

    def write_statement(self, s):
        format_string = ' '.join("%d" for _ in s.arguments) + r'\n'
        args = ', '.join(self.expression(v) for v in s.arguments)
        yield f'printf("{format_string}", {args});'

    def read_statement(self, statement):
        format_string = ''.join("%d" for _ in statement.arguments)
        args = ', '.join("&" + self.expression(v) for v in statement.arguments)
        yield f'scanf("{format_string}", {args});'

    def if_statement(self, s):
        condition = self.expression(s.condition)
        yield f"if( {condition} )" " {"
        yield from self.block_content(s.then_body)
        yield "}"
        if s.else_body is not None:
            yield "else {"
            yield from self.block_content(s.else_body)
            yield "}"

    def for_statement(self, s):
        index_name = s.index.variable.name
        size = self.expression(s.index.range)
        yield f"for(int {index_name} = 0; {index_name} < {size}; {index_name}++)" " {"
        yield from self.block_content(s.body)
        yield "}"

    def loop_statement(self, s):
        yield "while (true) {"
        yield from self.block_content(s.body)
        yield "}"

    def build_switch_condition(self, variable, labels):
        variable = self.expression(variable)
        result = f"{variable} == {self.expression(labels[0])}"
        for label in labels[1:]:
            result += f" || {variable} == {self.expression(label)}"
        return result

    def switch_statement(self, s):
        cases = [case for case in s.cases]
        yield f"if ({self.build_switch_condition(s.variable, cases[0].labels)}) " "{"
        yield from self.block_content(cases[0].body)
        for case in cases[1:]:
            yield "}" f" else if ({self.build_switch_condition(s.variable, case.labels)}) " "{"
            yield from self.block_content(case.body)
        if s.default:
            yield "} else {"
            yield from self.block_content(s.default)
        yield "}"

    def any_statement(self, s):
        generators = {
            "checkpoint": lambda: [r"""printf("%d\n", 0);"""],
            "flush": lambda: ["fflush(stdout);"],
            "exit": lambda: ["exit(0);"],
            "continue": lambda: ["continue;"],
            "break": lambda: ["break;"],
            "return": lambda: [f"return {self.expression(s.value)};"],
        }
        return generators[s.statement_type]()


class CppTemplateCodeGen(CppCodeGen):
    def var_statement(self, s):
        yield self.build_declaration(s)

    def function_statement(self, s):
        yield
        yield f"{self.build_callable_declarator(s.function)}" " {"
        yield self.indent("// TODO")
        yield "}"

    def callback_statement(self, s):
        callback = s.callback
        yield f"{self.build_callable_declarator(callback)};"
