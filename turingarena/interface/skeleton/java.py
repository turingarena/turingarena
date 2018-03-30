from turingarena.common import indent_all, indent
from turingarena.interface.skeleton.common import ExpressionBuilder, CodeGen
from turingarena.interface.context import StaticGlobalContext


def generate_skeleton_java(interface):
    yield from JavaSkeletonCodeGen(interface).generate()


def generate_template_java(interface):
    yield from JavaTemplateCodeGen(interface).generate()


class JavaSkeletonCodeGen(CodeGen):
    def generate(self):
        yield "import java.util.Scanner;"
        yield
        yield "abstract class Skeleton {"
        yield indent("private static final Scanner in = new Scanner(System.in);")
        yield
        yield from indent_all(self.block_content(self.interface.body))
        yield "}"
        yield

    def function_statement(self, statement):
        yield f"abstract {build_callable_declarator(statement.function)};"

    def callback_statement(self, statement):
        callback = statement.callback
        yield f"{build_callable_declarator(callback)}" " {"
        yield indent(f'System.out.println("{callback.name}");')
        yield from indent_all(self.block_content(statement.callback.body))
        yield "}"
        yield

    def main_statement(self, statement):
        yield
        yield "public static void main(String args[]) {"
        yield indent("Solution solution = new Solution();")
        yield from indent_all(self.block_content(statement.body))
        yield "}"

    def init_statement(self, statement):
        yield
        yield "static {"
        yield from indent_all(self.block_content(statement.body))
        yield "}"

    def alloc_statement(self, statement):
        size = build_expression(statement.size)
        for argument in statement.arguments:
            arg = build_expression(argument)
            yield f"{arg} = new {build_alloc_type(argument.value_type.item_type, size)};"

    def call_statement(self, statement):
        function_name = statement.function_name
        parameters = ", ".join(build_expression(p) for p in statement.parameters)
        if statement.return_value is not None:
            return_value = build_expression(statement.return_value)
            yield f"{return_value} = solution.{function_name}({parameters});"
        else:
            yield f"solution.{function_name}({parameters});"
        if statement.context.global_context.callbacks:
            yield 'System.out.println("return");'

    def output_statement(self, statement):
        format_string = ' '.join("%d" for _ in statement.arguments) + r'\n'
        args = ', '.join(build_expression(v) for v in statement.arguments)
        yield f'System.out.printf("{format_string}", {args});'

    def input_statement(self, statement):
        for arg in statement.arguments:
            yield f"{build_expression(arg)} = " + {
                int: "in.nextInt()",
            }[arg.value_type.base_type] + ";"

    def if_statement(self, statement):
        condition = build_expression(statement.condition)
        yield f"if ({condition})" " {"
        yield from indent_all(self.block_content(statement.then_body))
        if statement.else_body is not None:
            yield "} else {"
            yield from indent_all(self.block_content(statement.else_body))
        yield "}"

    def for_statement(self, statement):
        index_name = statement.index.variable.name
        size = build_expression(statement.index.range)
        yield f"for (int {index_name} = 0; {index_name} < {size}; {index_name}++)" " {"
        yield from indent_all(self.block_content(statement.body))
        yield "}"

    def var_statement(self, s):
        if isinstance(s.context, StaticGlobalContext):
            yield "static final " + build_declaration(s)
        else:
            yield build_declaration(s)

    def any_statement(self, statement):
        generators = {
            "flush": lambda: ["System.out.flush();"],
            "checkpoint": lambda: ["""System.out.println("0");"""],
            "exit": lambda: ["System.exit(0);"],
            "return": lambda: [f"return {build_expression(statement.value)};"],
        }
        return generators[statement.statement_type]()


class JavaTemplateCodeGen(CodeGen):
    def generate(self):
        yield "class Solution extends Skeleton {"
        yield from indent_all(self.block_content(self.interface.body))
        yield "}"

    def function_statement(self, statement):
        yield
        yield f"{build_callable_declarator(statement.function)}" " {"
        yield indent("// TODO")
        if statement.function.return_type:
            yield indent("return 0;")
        yield "}"


def build_callable_declarator(callable):
    return_type = build_type(callable.return_type)
    parameters = ', '.join(build_parameter(p) for p in callable.parameters)
    return f"{return_type} {callable.name}({parameters})"


def build_declaration(statement):
    type = build_type(statement.value_type)
    declarators = ', '.join(v.name for v in statement.variables)
    return f'{type} {declarators};'


def build_parameter(parameter):
    value_type = build_type(parameter.value_type)
    return f'{value_type} {parameter.name}'


def build_expression(expression):
    return ExpressionBuilder().build(expression)


def build_type(value_type):
    if value_type is None:
        return "void"
    builders = {
        "scalar": lambda: {
            int: "int",
        }[value_type.base_type],
        "array": lambda: f"{build_type(value_type.item_type)}[]"
    }
    return builders[value_type.meta_type]()


def build_alloc_type(var_type, size):
    if var_type.meta_type == "array":
        return build_alloc_type(var_type.item_type, size) + "[]"
    else:
        return {
            int: "int",
        }[var_type.base_type] + f"[{size}]"
