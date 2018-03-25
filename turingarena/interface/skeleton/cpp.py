from turingarena.common import indent_all, indent
from turingarena.interface.context import StaticGlobalContext
from turingarena.interface.skeleton.common import CodeGen


def generate_skeleton_cpp(interface):
    yield "#include <cstdio>"
    yield "#include <cstdlib>"
    yield from SkeletonCodeGen().block_content(interface)
    yield
    yield from generate_main(interface)


def generate_main(interface):
    yield "int main() {"
    for s in interface.statements:
        if s.statement_type in ("init", "main"):
            yield from indent_all(SkeletonCodeGen().block_content(s.body))
    yield "}"


def generate_template_cpp(interface):
    yield from TemplateCodeGen().block_content(interface)


class CppCodeGen(CodeGen):
    pass


class SkeletonCodeGen(CppCodeGen):
    def callback_statement(self, s):
        callback = s.callback
        yield f"{build_callable_declarator(callback)}" " {"
        yield indent(rf"""printf("%s\n", "{callback.name}");""")
        yield from indent_all(self.block_content(callback.body))
        yield "}"

    def function_statement(self, s):
        yield f"{build_callable_declarator(s.function)};"

    def var_statement(self, s):
        if isinstance(s.context, StaticGlobalContext):
            yield "extern " + build_declaration(s)
        else:
            yield build_declaration(s)

    def alloc_statement(self, s):
        for argument in s.arguments:
            arg = self.expression(argument)
            value_type = build_full_type(argument.value_type.item_type)
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
        if s.context.global_context.callbacks:
            yield r"""printf("return\n");"""

    def output_statement(self, s):
        format_string = ' '.join("%d" for _ in s.arguments) + r'\n'
        args = ', '.join(self.expression(v) for v in s.arguments)
        yield f'printf("{format_string}", {args});'

    def input_statement(self, statement):
        format_string = ''.join("%d" for _ in statement.arguments)
        args = ', '.join("&" + self.expression(v) for v in statement.arguments)
        yield f'scanf("{format_string}", {args});'

    def if_statement(self, s):
        condition = self.expression(s.condition)
        yield f"if( {condition} )" " {"
        yield from indent_all(self.block_content(s.then_body))
        yield "}"
        if s.else_body is not None:
            yield "else {"
            yield from indent_all(self.block_content(s.else_body))
            yield "}"

    def for_statement(self, s):
        index_name = s.index.variable.name
        size = self.expression(s.index.range)
        yield f"for(int {index_name} = 0; {index_name} < {size}; {index_name}++)" " {"
        yield from indent_all(self.block_content(s.body))
        yield "}"

    def any_statement(self, s):
        generators = {
            "checkpoint": lambda: [r"""printf("%d\n", 0);"""],
            "flush": lambda: ["fflush(stdout);"],
            "exit": lambda: ["exit(0);"],
            "return": lambda: [f"return {self.expression(s.value)};"],
            "main": lambda: [],
            "init": lambda: [],
        }
        return generators[s.statement_type]()


class TemplateCodeGen(CppCodeGen):
    def var_statement(self, s):
        yield build_declaration(s)

    def function_statement(self, s):
        yield f"{build_callable_declarator(s.function)}" " {"
        yield indent("// TODO")
        yield "}"

    def callback_statement(self, s):
        callback = s.callback
        yield f"{build_callable_declarator(callback)};"

    def any_statement(self, s):
        generators = {
            "var": lambda: ["extern " + build_declaration(s)],
            "init": lambda: [],
            "main": lambda: [],
        }
        return generators[s.statement_type]()


def generate_declarators(declaration):
    for variable in declaration.variables:
        yield build_declarator(declaration.value_type, variable.name)


def build_callable_declarator(callable):
    return_type = build_full_type(callable.return_type)
    arguments = ', '.join(build_parameter(p) for p in callable.parameters)
    return f"{return_type} {callable.name}({arguments})"


def build_declaration(statement):
    type_specifier = build_type_specifier(statement.value_type)
    declarators = ', '.join(generate_declarators(statement))
    return f'{type_specifier} {declarators};'


def build_parameter(parameter):
    full_type = build_full_type(parameter.value_type)
    return f'{full_type} {parameter.name}'


def build_declarator(value_type, name):
    if value_type is None:
        return name
    builders = {
        "scalar": lambda: name,
        "array": lambda: "*" + build_declarator(value_type.item_type, name),
    }
    return builders[value_type.meta_type]()


def build_type_specifier(value_type):
    if value_type is None:
        return "void"
    builders = {
        "scalar": lambda: {
            int: "int",
        }[value_type.base_type],
        "array": lambda: build_type_specifier(value_type.item_type)
    }
    return builders[value_type.meta_type]()


def build_full_type(value_type):
    return build_type_specifier(value_type) + build_declarator(value_type, "")
