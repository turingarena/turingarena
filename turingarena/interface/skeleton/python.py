from turingarena.common import indent_all, indent
from turingarena.interface.skeleton.common import ExpressionBuilder


def generate_skeleton_python(interface):
    for statement in interface.statements:
        yield
        yield from generate_skeleton_statement(statement)
    yield
    yield f"import source as _source"


def generate_template_python(interface):
    for statement in interface.statements:
        yield
        yield from generate_template_statement(statement)


def generate_skeleton_statement(statement):
    generators = {
        "var": lambda: generate_var(statement),
        "function": lambda: [],
        "callback": lambda: generate_callback(statement),
        "init": lambda: generate_init(statement),
        "main": lambda: generate_main(statement),
    }

    return generators[statement.statement_type]()


def generate_template_statement(statement):
    generators = {
        "var": lambda: generate_global_var_template(statement),
        "function": lambda: generate_function_template(statement),
        "callback": lambda: generate_callback_template(statement),
        "main": lambda: [],
        "init": lambda: [],
    }
    return generators[statement.statement_type]()


def generate_var(statement):
    names = ", ".join(d.name for d in statement.variables)
    formats = ", ".join(build_type(d.value_type) for d in statement.variables)
    yield f"# {names} : {formats}"


def generate_global_var_template(statement):
    names = ", ".join(v.name for v in statement.variables)
    yield f"from skeleton import {names}"


def generate_function_template(statement):
    function = statement.function
    yield f"def {build_callable_declarator(function)}:"
    yield indent("# TODO")
    yield indent("pass")


def generate_globals(context):
    if context.global_variables:
        variables = ", ".join(v.name for v in context.global_variables)
        yield f"global {variables}"


def generate_callback(statement):
    callback = statement.callback
    yield f"def {build_callable_declarator(callback)}:"
    yield from indent_all(generate_globals(statement.context))
    yield indent(f"print('{callback.name}')")
    yield from indent_all(generate_block(callback.body))


def generate_callback_template(statement):
    callback = statement.callback
    yield f"from skeleton import {callback.name}"


def generate_init(statement):
    yield from generate_block(statement.body)


def generate_main(statement):
    yield 'def main():'
    yield from indent_all(generate_globals(statement.context))
    yield from indent_all(generate_block(statement.body))


def generate_block(block):
    for statement in block.statements:
        yield from generate_block_statement(statement)


def generate_block_statement(statement):
    generators = {
        "var": lambda: generate_var(statement),
        "alloc": lambda: generate_alloc(statement),
        "input": lambda: generate_input(statement),
        "output": lambda: generate_output(statement),
        "checkpoint": lambda: ["""print(0)"""],
        "flush": lambda: ["""print(end="", flush=True)"""],
        "call": lambda: generate_call(statement),
        "for": lambda: generate_for(statement),
        "if": lambda: generate_if(statement),
        "exit": lambda: ["raise SystemExit"],
        "return": lambda: [f"return {build_expression(statement.value)}"],
    }
    return generators[statement.statement_type]()


def generate_alloc(statement):
    for argument in statement.arguments:
        arg = build_expression(argument)
        size = build_expression(statement.size)
        yield f"{arg} = [None] * {size}"


def generate_call(statement):
    function_name = statement.function_name
    parameters = ", ".join(build_expression(p) for p in statement.parameters)
    if statement.return_value is not None:
        return_value = build_expression(statement.return_value)
        yield f"{return_value} = _source.{function_name}({parameters})"
    else:
        yield f"_source.{function_name}({parameters})"
    if statement.context.global_context.callbacks:
        yield r"""print("return")"""


def generate_output(statement):
    args = ', '.join(build_expression(v) for v in statement.arguments)
    yield f'print({args})'


def generate_input(statement):
    arguments = ", ".join(
        build_expression(v)
        for v in statement.arguments
    )

    yield f"[{arguments}] = map(int, input().split())"


def generate_if(statement):
    condition = build_expression(statement.condition)
    yield f"if {condition}:"
    yield from indent_all(generate_block(statement.then_body))
    if statement.else_body is None:
        return
    yield "else:"
    yield from indent_all(generate_block(statement.else_body))


def generate_for(statement):
    index_name = statement.index.variable.name
    size = build_expression(statement.index.range)
    yield f"for {index_name} in range({size}):"
    yield from indent_all(generate_block(statement.body))


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
