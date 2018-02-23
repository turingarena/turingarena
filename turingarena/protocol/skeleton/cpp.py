import os

from turingarena.common import write_to_file, indent_all, indent


def generate_skeleton(*, interface_definition, dest_dir):
    with open(os.path.join(dest_dir, "skeleton.cpp"), "w") as main_file:
        write_to_file(generate_main_file(interface_definition), main_file)
    with open(os.path.join(dest_dir, "template.cpp"), "w") as template_file:
        write_to_file(generate_template_file(interface_definition), template_file)


def generate_main_file(interface):
    yield "#include <cstdio>"
    yield "#include <cstdlib>"
    for statement in interface.body.statements:
        yield
        yield from generate_skeleton_statement(statement, interface=interface)


def generate_template_file(interface):
    for statement in interface.body.statements:
        yield
        yield from generate_template_statement(statement, interface=interface)


def generate_skeleton_statement(statement, *, interface):
    generators = {
        "var": lambda: ["extern " + build_declaration(statement)],
        "function": lambda: generate_function(statement),
        "callback": lambda: generate_callback(statement, interface=interface),
        "main": lambda: generate_main(statement, interface=interface),
    }
    return generators[statement.statement_type]()


def generate_template_statement(statement, *, interface):
    generators = {
        "var": lambda: [build_declaration(statement)],
        "function": lambda: generate_function_template(statement),
        "callback": lambda: generate_callback_template(statement, interface=interface),
        "main": lambda: [],
    }
    return generators[statement.statement_type]()


def generate_function(statement):
    yield f"{build_callable_declarator(statement.function)};"


def generate_function_template(statement):
    yield f"{build_callable_declarator(statement.function)}" " {"
    yield indent("// TODO")
    yield "}"


def generate_callback(statement, *, interface):
    callback = statement.callback
    yield f"{build_callable_declarator(callback)}" " {"
    yield indent(rf"""printf("%s\n", "{callback.name}");""")
    yield from indent_all(generate_block(callback.body, interface=interface))
    yield "}"


def generate_callback_template(statement, *, interface):
    callback = statement.callback
    yield f"{build_callable_declarator(callback)};"


def generate_main(statement, *, interface):
    yield "int main() {"
    yield from indent_all(generate_block(statement.main.body, interface=interface))
    yield "}"


def generate_block(block, *, interface):
    for statement in block.statements:
        yield from generate_block_statement(statement, interface=interface)


def generate_block_statement(statement, *, interface):
    generators = {
        "var": lambda: [build_declaration(statement)],
        "alloc": lambda: generate_alloc(statement),
        "input": lambda: generate_input(statement),
        "output": lambda: generate_output(statement),
        "flush": lambda: ["fflush(stdout);"],
        "call": lambda: generate_call(statement, interface=interface),
        "for": lambda: generate_for(statement, interface=interface),
        "if": lambda: generate_if(statement, interface=interface),
        "exit": lambda: ["exit(0);"],
        "return": lambda: [f"return {build_expression(statement.value)};"],
    }
    return generators[statement.statement_type]()


def generate_declarators(declaration):
    for variable in declaration.variables:
        yield build_declarator(declaration.value_type, variable.name)


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
    format_string = ' '.join(build_format(v) for v in statement.arguments) + r'\n'
    args = ', '.join(build_expression(v) for v in statement.arguments)
    yield f'printf("{format_string}", {args});'


def generate_input(statement):
    format_string = ''.join(build_format(v) for v in statement.arguments)
    args = ', '.join("&" + build_expression(v) for v in statement.arguments)
    yield f'scanf("{format_string}", {args});'


def generate_if(statement, *, interface):
    condition = build_expression(statement.condition)
    yield f"if( {condition} )" " {"
    yield from indent_all(generate_block(statement.then_body, interface=interface))
    yield "}"
    if statement.else_body is not None:
        yield "else {"
        yield from indent_all(generate_block(statement.else_body, interface=interface))
        yield "}"


def generate_for(statement, *, interface):
    index_name = statement.index.variable.name
    size = build_expression(statement.index.range)
    yield f"for(int {index_name} = 0; {index_name} < {size}; {index_name}++)" " {"
    yield from indent_all(generate_block(statement.body, interface=interface))
    yield "}"


def build_callable_declarator(callable):
    signature = callable.signature
    return_type = build_full_type(signature.return_type)
    arguments = ', '.join(build_parameter(p) for p in signature.parameters)
    return f"{return_type} {callable.name}({arguments})"


def build_declaration(statement):
    type_specifier = build_type_specifier(statement.value_type)
    declarators = ', '.join(generate_declarators(statement))
    return f'{type_specifier} {declarators};'


def build_parameter(parameter):
    full_type = build_full_type(parameter.value_type)
    declarator = build_declarator(parameter.value_type, parameter.name)
    return f'{full_type} {declarator}'


def build_subscript(expression):
    array = build_expression(expression.array)
    index = build_expression(expression.index)
    return f"{array}[{index}]"


def build_expression(expression):
    builders = {
        "int_literal": lambda: f"{expression.value}",
        "reference": lambda: f"{expression.variable.name}",
        "subscript": lambda: build_subscript(expression),
    }
    return builders[expression.expression_type]()


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


def build_format(expr):
    return {
        int: "%d",
    }[expr.value_type.base_type]
