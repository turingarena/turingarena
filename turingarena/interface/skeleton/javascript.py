from turingarena.common import indent_all, indent
from turingarena.interface.skeleton.common import ExpressionBuilder


def generate_skeleton_javascript(interface):
    yield "async function init() {}"
    for statement in interface.body.statements:
        yield from generate_skeleton_statement(statement)


def generate_template_javascript(interface):
    for statement in interface.body.statements:
        yield
        yield from generate_template_statement(statement)


def generate_skeleton_statement(statement):
    generators = {
        "var": lambda: generate_var(statement),
        "function": lambda: [],
        "callback": lambda: generate_callback(statement),
        "main": lambda: generate_main(statement),
        "init": lambda: generate_init(statement),
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
    names = ", ".join(v.name for v in statement.variables)
    yield f"let {names};"


def generate_global_var_template(statement):
    names = ", ".join(v.name for v in statement.variables)
    yield f"// global var: {names}"


def generate_function_template(statement):
    fun = statement.function
    yield f"function {build_callable_declarator(fun)}" + "{"
    yield indent("// TODO")
    yield "}"


def generate_callback(statement):
    callback = statement.callback
    yield f"function {build_callable_declarator(callback)}" + "{"
    yield indent(f"print('{callback.name}');")
    yield from indent_all(generate_block(callback.body))
    yield "}"
    yield


def generate_callback_template(statement):
    yield f"// callback {statement.callback.name}"


def generate_main(statement):
    yield "async function main() {"
    yield indent("__load_source__(); // load user source file")
    yield from indent_all(generate_block(statement.body))
    yield "}"


def generate_init(statement):
    yield "async function init() {"
    yield from indent_all(generate_block(statement.body))
    yield "}"


def generate_block(block):
    for statement in block.statements:
        yield from generate_block_statement(statement)


def generate_block_statement(statement):
    generators = {
        "var": lambda: generate_var(statement),
        "alloc": lambda: generate_alloc(statement),
        "input": lambda: generate_input(statement),
        "output": lambda: generate_output(statement),
        "checkpoint": lambda: ["print(0);"],
        "flush": lambda: ["flush();"],
        "call": lambda: generate_call(statement),
        "for": lambda: generate_for(statement),
        "if": lambda: generate_if(statement),
        "exit": lambda: ["exit(0);"],
        "return": lambda: [f"return {build_expression(statement.value)};"],
    }
    return generators[statement.statement_type]()


def generate_alloc(statement):
    for argument in statement.arguments:
        arg = build_expression(argument)
        size = build_expression(statement.size)
        yield f"{arg} = Array({size});"


def generate_call(statement):
    function_name = statement.function.name
    parameters = ", ".join(build_expression(p) for p in statement.parameters)
    if statement.return_value is not None:
        return_value = build_expression(statement.return_value)
        yield f"{return_value} = {function_name}({parameters});"
    else:
        yield f"{function_name}({parameters});"
    if statement.context.global_context.callbacks:
        yield "print('return');"


def generate_output(statement):
    args = ", ".join(build_expression(v) for v in statement.arguments)
    yield f"print({args});"


def generate_input(statement):
    args = ", ".join(build_expression(arg) for arg in statement.arguments)
    yield f"[{args}] = await readIntegers();"


def generate_if(statement):
    condition = build_expression(statement.condition)
    yield f"if ({condition})" " {"
    yield from indent_all(generate_block(statement.then_body))
    if statement.else_body is not None:
        yield "} else {"
        yield from indent_all(generate_block(statement.else_body))
    yield "}"


def generate_for(statement):
    index_name = statement.index.variable.name
    size = build_expression(statement.index.range)
    yield f"for (let {index_name} = 0; {index_name} < {size}; {index_name}++)" " {"
    yield from indent_all(generate_block(statement.body))
    yield "}"


def build_callable_declarator(callable):
    arguments = ", ".join(build_parameter(p) for p in callable.parameters)
    return f"{callable.name}({arguments})"


def build_parameter(parameter):
    return f"{parameter.name}"


def build_expression(expression):
    return ExpressionBuilder().build(expression)
