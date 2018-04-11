from turingarena.interface.context import StaticGlobalContext
from turingarena.sandbox.languages.generator import CodeGen


class JavaCodeGen(CodeGen):
    @classmethod
    def build_callable_declarator(cls, callable):
        return_type = cls.build_type(callable.return_type)
        parameters = ', '.join(cls.build_parameter(p) for p in callable.parameters)
        return f"{return_type} {callable.name}({parameters})"

    @classmethod
    def build_declaration(cls, statement):
        type = cls.build_type(statement.value_type)
        declarators = ', '.join(v.name for v in statement.variables)
        return f'{type} {declarators};'

    @classmethod
    def build_parameter(cls, parameter):
        value_type = cls.build_type(parameter.value_type)
        return f'{value_type} {parameter.name}'

    @classmethod
    def build_type(cls, value_type):
        if value_type is None:
            return "void"
        builders = {
            "scalar": lambda: {
                int: "int",
            }[value_type.base_type],
            "array": lambda: f"{cls.build_type(value_type.item_type)}[]"
        }
        return builders[value_type.meta_type]()

    @classmethod
    def build_alloc_type(cls, var_type, size):
        if var_type.meta_type == "array":
            return cls.build_alloc_type(var_type.item_type, size) + "[]"
        else:
            return {
                       int: "int",
                   }[var_type.base_type] + f"[{size}]"


class JavaSkeletonCodeGen(JavaCodeGen):
    def generate(self):
        yield "import java.util.Scanner;"
        yield
        yield "abstract class Skeleton {"
        yield self.indent("private static final Scanner in = new Scanner(System.in);")
        yield
        yield from self.block_content(self.interface.body)
        yield "}"
        yield

    def function_statement(self, statement):
        yield f"abstract {self.build_callable_declarator(statement.function)};"

    def callback_statement(self, statement):
        callback = statement.callback
        yield f"{self.build_callable_declarator(callback)}" " {"
        yield self.indent(f'System.out.println("{callback.name}");')
        yield from self.block_content(statement.callback.body)
        yield "}"
        yield

    def main_statement(self, statement):
        yield
        yield "public static void main(String args[]) {"
        yield self.indent("Solution solution = new Solution();")
        yield from self.block_content(statement.body)
        yield "}"

    def init_statement(self, statement):
        yield
        yield "static {"
        yield from self.block_content(statement.body)
        yield "}"

    def alloc_statement(self, statement):
        size = self.expression(statement.size)
        for argument in statement.arguments:
            arg = self.expression(argument)
            yield f"{arg} = new {self.build_alloc_type(argument.value_type.item_type, size)};"

    def call_statement(self, statement):
        function_name = statement.function_name
        parameters = ", ".join(self.expression(p) for p in statement.parameters)
        if statement.return_value is not None:
            return_value = self.expression(statement.return_value)
            yield f"{return_value} = solution.{function_name}({parameters});"
        else:
            yield f"solution.{function_name}({parameters});"
        if statement.context.global_context.callbacks:
            yield 'System.out.println("return");'

    def write_statement(self, statement):
        format_string = ' '.join("%d" for _ in statement.arguments) + r'\n'
        args = ', '.join(self.expression(v) for v in statement.arguments)
        yield f'System.out.printf("{format_string}", {args});'

    def read_statement(self, statement):
        for arg in statement.arguments:
            yield f"{self.expression(arg)} = " + {
                int: "in.nextInt()",
            }[arg.value_type.base_type] + ";"

    def if_statement(self, statement):
        condition = self.expression(statement.condition)
        yield f"if ({condition})" " {"
        yield from self.block_content(statement.then_body)
        if statement.else_body is not None:
            yield "} else {"
            yield from self.block_content(statement.else_body)
        yield "}"

    def for_statement(self, statement):
        index_name = statement.index.variable.name
        size = self.expression(statement.index.range)
        yield f"for (int {index_name} = 0; {index_name} < {size}; {index_name}++)" " {"
        yield from self.block_content(statement.body)
        yield "}"

    def var_statement(self, s):
        if isinstance(s.context, StaticGlobalContext):
            yield "static final " + self.build_declaration(s)
        else:
            yield self.build_declaration(s)

    def loop_statement(self, s):
        yield "while (true) {"
        yield from self.block_content(s.body)
        yield "}"

    def switch_statement(self, s):
        yield f"switch ({self.expression(s.value)}) " "{"
        for case in s.cases:
            yield from self.case_statement(case)
        if s.default:
            yield "default: "
            yield from self.block_content(s.default)
        yield "}"

    def case_statement(self, s):
        yield f"case {self.expression(s.label)}:"
        yield from self.block_content(s.body)

    def any_statement(self, statement):
        generators = {
            "flush": lambda: ["System.out.flush();"],
            "checkpoint": lambda: ["""System.out.println("0");"""],
            "exit": lambda: ["System.exit(0);"],
            "return": lambda: [f"return {self.expression(statement.value)};"],
            "continue": lambda: ["continue;"],
            "break": lambda: ["break;"],
        }
        return generators[statement.statement_type]()


class JavaTemplateCodeGen(JavaCodeGen):
    def generate(self):
        yield "class Solution extends Skeleton {"
        yield from self.block_content(self.interface.body)
        yield "}"

    def function_statement(self, statement):
        yield
        yield f"{self.build_callable_declarator(statement.function)}" " {"
        yield self.indent("// TODO")
        yield "}"
