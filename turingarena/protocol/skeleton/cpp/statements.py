from turingarena.tools.utils import indent_all, indent
from turingarena.protocol.skeleton.cpp.expressions import build_expression
from turingarena.protocol.skeleton.cpp.type_expressions import build_full_type, build_declarator, build_type_specifier


def generate_format(expr):
    return {
        int: "%d",
        bool: "%d",
    }[expr.value_type.base_type]


def generate_alloc(statement):
    for argument in statement.arguments:
        arg = build_expression(argument)
        value_type = build_full_type(argument.value_type.item_type)
        size = build_expression(statement.size)
        yield f"{arg} = new {value_type}[{size}];"


def generate_call(statement, *, interface):
    function_name = statement.function.name
    parameters = ", ".join(build_expression(p) for p in statement.parameters)
    if statement.return_value is not None:
        return_value = build_expression(statement.return_value)
        yield f"{return_value} = {function_name}({parameters});"
    else:
        yield f"{function_name}({parameters});"
    if interface.signature.callbacks:
        yield r"""printf("return\n");"""


def generate_output(statement):
    format_string = ' '.join(generate_format(v) for v in statement.arguments) + r'\n'
    args = ', '.join(build_expression(v) for v in statement.arguments)
    yield f'printf("{format_string}", {args});'


def generate_input(statement):
    format_string = ''.join(generate_format(v) for v in statement.arguments)
    args = ', '.join("&" + build_expression(v) for v in statement.arguments)
    yield f'scanf("{format_string}", {args});'


def generate_if(statement, *, interface):
    condition = build_expression(statement.condition)
    yield f"if( {condition} )" " {"
    yield from indent_all(generate_block(statement.then_body, interface=interface))
    yield "}"
    if hasattr(statement, 'else_body'):
        yield "else {"
        yield from indent_all(generate_block(statement.else_body, interface=interface))
        yield "}"


def generate_for(statement, *, interface):
    index_name = statement.index.variable.name
    size = build_expression(statement.index.range)
    yield f"for(int {index_name} = 0; {index_name} < {size}; {index_name}++)" " {"
    yield from indent_all(generate_block(statement.body, interface=interface))
    yield "}"


def generate_main(statement, *, interface):
    yield "int main() {"
    yield from indent_all(generate_block(statement.main.body, interface=interface))
    yield "}"


def generate_callback(statement, *, interface):
    callback = statement.callback
    yield f"{build_callable_declarator(callback)}" " {"
    yield indent(rf"""printf("%s\n", "{callback.name}");""")
    yield from indent_all(generate_block(callback.body, interface=interface))
    yield "}"


def build_callable_declarator(callable):
    signature = callable.signature
    return_type = build_full_type(signature.return_type)
    arguments = ', '.join(build_parameter(p) for p in signature.parameters)
    return f"{return_type} {callable.name}({arguments})"


def generate_function(statement):
    yield f"{build_callable_declarator(statement.function)};"


def generate_block(block, *, interface):
    for statement in block.statements:
        yield from generate_statement(statement, interface=interface)


def generate_statement(statement, *, interface):
    generators = {
        "var": lambda: [build_declaration(statement)],
        "function": lambda: generate_function(statement),
        "callback": lambda: generate_callback(statement, interface=interface),
        "main": lambda: generate_main(statement, interface=interface),
        "alloc": lambda: generate_alloc(statement),
        "input": lambda: generate_input(statement),
        "output": lambda: generate_output(statement),
        "flush": lambda: ["fflush(stdout);"],
        "call": lambda: generate_call(statement, interface=interface),
        "for": lambda: generate_for(statement, interface=interface),
        "exit": lambda: ["exit(0);"],
        "return": lambda: [f"return {build_expression(statement.value)};"],
    }
    return generators[statement.statement_type]()


def generate_declarators(declaration):
    for variable in declaration.variables:
        yield build_declarator(declaration.value_type, variable.name)


def build_declaration(statement):
    type_specifier = build_type_specifier(statement.value_type)
    declarators = ', '.join(generate_declarators(statement))
    return f'{type_specifier} {declarators};'


def build_parameter(parameter):
    full_type = build_full_type(parameter.value_type)
    declarator = build_declarator(parameter.value_type, parameter.name)
    return f'{full_type} {declarator}'
