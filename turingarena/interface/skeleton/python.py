from turingarena.common import indent_all, indent
from turingarena.interface.skeleton.common import ExpressionBuilder, CodeGen


def generate_skeleton_python(interface):
    yield from PythonSkeletonCodeGen(interface).generate()


def generate_template_python(interface):
    yield from PythonTemplateCodeGen(interface).generate()


class PythonSkeletonCodeGen(CodeGen):
    def generate(self):
        yield from self.block_content(self.interface.body)
        yield
        yield "import source as _source"

    def var_statement(self, statement):
        names = ", ".join(d.name for d in statement.variables)
        formats = ", ".join(build_type(d.value_type) for d in statement.variables)
        yield f"# {names} : {formats}"

    def callback_statement(self, statement):
        callback = statement.callback
        yield f"def {build_callable_declarator(callback)}:"
        yield from indent_all(generate_globals(statement.context))
        yield indent(f"print('{callback.name}')")
        yield from indent_all(self.block_content(callback.body))

    def init_statement(self, statement):
        yield
        yield "# init block"
        yield from self.block_content(statement.body)

    def main_statement(self, statement):
        yield
        yield 'def main():'
        yield from indent_all(generate_globals(statement.context))
        yield from indent_all(self.block_content(statement.body))

    def any_statement(self, statement):
        generators = {
            "checkpoint": lambda: ["""print(0)"""],
            "flush": lambda: ["""print(end="", flush=True)"""],
            "exit": lambda: ["raise SystemExit"],
            "return": lambda: [f"return {build_expression(statement.value)}"],
            "function": lambda: [],
        }
        return generators[statement.statement_type]()

    def alloc_statement(self, statement):
        for argument in statement.arguments:
            arg = build_expression(argument)
            size = build_expression(statement.size)
            yield f"{arg} = [None] * {size}"

    def call_statement(self, statement):
        function_name = statement.function_name
        parameters = ", ".join(build_expression(p) for p in statement.parameters)
        if statement.return_value is not None:
            return_value = build_expression(statement.return_value)
            yield f"{return_value} = _source.{function_name}({parameters})"
        else:
            yield f"_source.{function_name}({parameters})"
        if statement.context.global_context.callbacks:
            yield r"""print("return")"""

    def output_statement(self, statement):
        args = ', '.join(build_expression(v) for v in statement.arguments)
        yield f'print({args})'

    def input_statement(self, statement):
        arguments = ", ".join(
            build_expression(v)
            for v in statement.arguments
        )

        yield f"[{arguments}] = map(int, input().split())"

    def if_statement(self, statement):
        condition = build_expression(statement.condition)
        yield f"if {condition}:"
        yield from indent_all(self.block_content(statement.then_body))
        if statement.else_body is None:
            return
        yield "else:"
        yield from indent_all(self.block_content(statement.else_body))

    def for_statement(self, statement):
        index_name = statement.index.variable.name
        size = build_expression(statement.index.range)
        yield f"for {index_name} in range({size}):"
        yield from indent_all(self.block_content(statement.body))


class PythonTemplateCodeGen(CodeGen):
    def function_statement(self, statement):
        yield
        yield f"def {build_callable_declarator(statement.function)}:"
        yield indent("# TODO")
        yield indent("pass")


def generate_globals(context):
    if context.global_variables:
        variables = ", ".join(v.name for v in context.global_variables)
        yield f"global {variables}"


def generate_callback_template(statement):
    callback = statement.callback
    yield f"from skeleton import {callback.name}"


def build_callable_declarator(callable):
    arguments = ', '.join(build_parameter(p) for p in callable.parameters)
    return f"{callable.name}({arguments})"


def build_parameter(parameter):
    return f'{parameter.name}'


def build_expression(expression):
    return ExpressionBuilder().build(expression)


def build_type(t):
    builders = {
        "scalar": lambda: f"int",
        "array": lambda: f"List[{build_type(t.item_type)}]",
    }
    return builders[t.meta_type]()
