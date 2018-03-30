from turingarena.common import indent_all, indent
from turingarena.interface.skeleton.common import ExpressionBuilder, CodeGen


class JavaScriptSkeletonCodeGen(CodeGen):
    def generate(self):
        yield "async function init() {}"
        yield from self.block_content(self.interface.body)

    def var_statement(self, statement):
        names = ", ".join(v.name for v in statement.variables)
        yield f"let {names};"

    def callback_statement(self, statement):
        callback = statement.callback
        yield f"function {build_callable_declarator(callback)}" + "{"
        yield indent(f"print('{callback.name}');")
        yield from indent_all(self.block_content(callback.body))
        yield "}"
        yield

    def main_statement(self, statement):
        yield
        yield "async function main() {"
        yield indent("__load_source__(); // load user source file")
        yield from indent_all(self.block_content(statement.body))
        yield "}"

    def init_statement(self, statement):
        yield
        yield "async function init() {"
        yield from indent_all(self.block_content(statement.body))
        yield "}"

    def any_statement(self, statement):
        generators = {
            "checkpoint": lambda: ["print(0);"],
            "flush": lambda: ["flush();"],
            "exit": lambda: ["exit(0);"],
            "return": lambda: [f"return {build_expression(statement.value)};"],
            "function": lambda: [],
        }
        return generators[statement.statement_type]()

    def call_statement(self, statement):
        function_name = statement.function.name
        parameters = ", ".join(build_expression(p) for p in statement.parameters)
        if statement.return_value is not None:
            return_value = build_expression(statement.return_value)
            yield f"{return_value} = {function_name}({parameters});"
        else:
            yield f"{function_name}({parameters});"
        if statement.context.global_context.callbacks:
            yield "print('return');"

    def alloc_statement(self, statement):
        for argument in statement.arguments:
            arg = build_expression(argument)
            size = build_expression(statement.size)
            yield f"{arg} = Array({size});"

    def output_statement(self, statement):
        args = ", ".join(build_expression(v) for v in statement.arguments)
        yield f"print({args});"

    def input_statement(self, statement):
        args = ", ".join(build_expression(arg) for arg in statement.arguments)
        yield f"[{args}] = await readIntegers();"

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
        yield f"for (let {index_name} = 0; {index_name} < {size}; {index_name}++)" " {"
        yield from indent_all(self.block_content(statement.body))
        yield "}"


class JavaScriptTemplateCodeGen(CodeGen):
    def function_statement(self, statement):
        yield
        yield f"function {build_callable_declarator(statement.function)}" + "{"
        yield indent("// TODO")
        yield "}"


def build_callable_declarator(callable):
    arguments = ", ".join(build_parameter(p) for p in callable.parameters)
    return f"{callable.name}({arguments})"


def build_parameter(parameter):
    return f"{parameter.name}"


def build_expression(expression):
    return ExpressionBuilder().build(expression)
