from turingarena.common import indent_all, indent


def generate_skeleton_python(interface):
    yield "import sys"
    for statement, context in interface.contextualized_statements():
        yield
        yield from generate_skeleton_statement(statement, context=context)
    yield
    yield f"__load_source__()"
    yield f"import source as _source"


def generate_template_python(interface):
    for statement, context in interface.contextualized_statements():
        yield
        yield from generate_template_statement(statement, context=context)


def generate_skeleton_statement(statement, *, context):
    generators = {
        "var": lambda: generate_var(statement),
        "function": lambda: [],
        "callback": lambda: generate_callback(statement, context=context),
        "init": lambda: generate_init(statement, context=context),
        "main": lambda: generate_main(statement, context=context),
    }

    return generators[statement.statement_type]()


def generate_template_statement(statement, *, context):
    generators = {
        "var": lambda: generate_global_var_template(statement),
        "function": lambda: generate_function_template(statement),
        "callback": lambda: generate_callback_template(statement, context=context),
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
        variables = ", ".join(context.global_variables)
        yield f"global {variables}"


def generate_callback(statement, *, context):
    callback = statement.callback
    yield f"def {build_callable_declarator(callback)}:"
    yield from indent_all(generate_globals(context))
    yield indent(f"print('{callback.name}')")
    yield from indent_all(generate_block(callback.body, context=context))


def generate_callback_template(statement, *, context):
    callback = statement.callback
    yield f"from skeleton import {callback.name}"


def generate_init(statement, *, context):
    yield from generate_block(statement.init.body, context=context)


def generate_main(statement, *, context):
    yield 'def main():'
    yield from indent_all(generate_globals(context))
    yield from indent_all(generate_block(statement.main.body, context=context))


def generate_block(block, *, context):
    for statement in block.statements:
        yield from generate_block_statement(statement, context=context)


def generate_block_statement(statement, *, context):
    generators = {
        "var": lambda: generate_var(statement),
        "alloc": lambda: generate_alloc(statement),
        "input": lambda: generate_input(statement),
        "output": lambda: generate_output(statement),
        "checkpoint": lambda: ["""print(0)"""],
        "flush": lambda: ["""sys.stdout.flush()"""],
        "call": lambda: generate_call(statement, context=context),
        "for": lambda: generate_for(statement, context=context),
        "if": lambda: generate_if(statement, context=context),
        "exit": lambda: ["sys.exit(0)"],
        "return": lambda: [f"return {build_expression(statement.value)}"],
    }
    return generators[statement.statement_type]()


def generate_alloc(statement):
    for argument in statement.arguments:
        arg = build_expression(argument)
        size = build_expression(statement.size)
        yield f"{arg} = [None] * {size}"


def generate_call(statement, *, context):
    function_name = statement.function.name
    parameters = ", ".join(build_expression(p) for p in statement.parameters)
    if statement.return_value is not None:
        return_value = build_expression(statement.return_value)
        yield f"{return_value} = _source.{function_name}({parameters})"
    else:
        yield f"_source.{function_name}({parameters})"
    if context.scope.callbacks:
        yield r"""print("return")"""


def generate_output(statement):
    args = ', '.join(build_expression(v) for v in statement.arguments)
    yield f'print({args})'


def generate_input(statement):
    arguments = ", ".join(
        build_expression(v)
        for v in statement.arguments
    )

    formats = ", ".join(
        "int" for v in statement.arguments
    )

    yield f"[{arguments}] = (fmt(v) for fmt, v in zip([{formats}], sys.stdin.readline().split()))"


def generate_if(statement, *, context):
    condition = build_expression(statement.condition)
    yield f"if {condition}:"
    yield from indent_all(generate_block(statement.then_body, context=context))
    if statement.else_body is None:
        return
    yield "else:"
    yield from indent_all(generate_block(statement.else_body, context=context))


def generate_for(statement, *, context):
    index_name = statement.index.variable.name
    size = build_expression(statement.index.range)
    yield f"for {index_name} in range({size}):"
    body, body_context = statement.contextualized_body(context)
    yield from indent_all(generate_block(body, context=body_context))


def build_callable_declarator(callable):
    signature = callable.signature
    arguments = ', '.join(build_parameter(p) for p in signature.parameters)
    return f"{callable.name}({arguments})"


def build_parameter(parameter):
    return f'{parameter.name}'


def build_subscript(expression):
    array = build_expression(expression.array)
    index = build_expression(expression.index)
    return f"{array}[{index}]"


def build_expression(expression):
    builders = {
        "int_literal": lambda: f"{expression.value}",
        "reference": lambda: f"{expression.variable_name}",
        "subscript": lambda: build_subscript(expression),
    }
    return builders[expression.expression_type]()


def build_type(t):
    builders = {
        "scalar": lambda: f"int",
        "array": lambda: f"List[{build_type(t.item_type)}]",
    }
    return builders[t.meta_type]()
